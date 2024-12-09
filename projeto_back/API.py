from flask import Flask, request, jsonify, send_file
from urllib.parse import unquote
import matplotlib.pyplot as plt
import re
import importlib
import io
import bot_email
import secrets
import database
import hashlib
from apscheduler.schedulers.background import BackgroundScheduler
from math import radians, sin, cos, sqrt, atan2
from datetime import datetime, timedelta
import threading

def calcular_distancia(lat1, lng1, lat2, lng2):
    R = 6371.0  # Raio da Terra em km
    dlat = radians(lat2 - lat1)
    dlng = radians(lng2 - lng1)
    a = sin(dlat / 2)**2 + cos(radians(lat1)) * cos(radians(lat2)) * sin(dlng / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    return R * c

def excluir_usuarios_expirados():
    cursor = database.conexao.cursor()
    cursor.execute("SELECT user_email, created_at, is_validated FROM users")
    usuarios = cursor.fetchall()

    for usuario in usuarios:
        email, created_at, is_validated = usuario
        if not is_validated and created_at and datetime.now() > created_at + timedelta(minutes=15):
            database.excluir_usuario(email)
            print(f"Usuário {email} excluído por expiração do token.")

scheduler = BackgroundScheduler()
scheduler.add_job(excluir_usuarios_expirados, 'interval', minutes=1)
scheduler.start()


app = Flask(__name__, static_folder="static")
class TimeoutException(Exception):
    pass

def run_with_timeout(func, timeout, *args, **kwargs):
    result = {}

    def wrapper():
        try:
            result["value"] = func(*args, **kwargs)
        except Exception as e:
            result["exception"] = e

    thread = threading.Thread(target=wrapper)
    thread.start()
    thread.join(timeout)

    if thread.is_alive():
        raise TimeoutException("Tempo limite atingido")
    if "exception" in result:
        raise result["exception"]
    return result.get("value")


@app.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    senha = data.get('senha')

    # Verifica se os campos obrigatórios estão presentes
    if not email or not senha:
        return jsonify({"status": "fail", "reason": "Email ou senha faltando"}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        return jsonify({"status": "fail", "reason": "Usuário não encontrado"}), 404

    # Verifica a senha
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    if usuario['user_password'] != senha_hash:
        return jsonify({"status": "fail", "reason": "Senha incorreta"}), 401

    # Login bem-sucedido
    return jsonify({"status": "success", "message": "Login realizado com sucesso"}), 200


@app.route('/enviar-email', methods=['POST'])
def enviar_email():
    data = request.json
    nome_usuario = data.get('nome_usuario')
    email = data.get('email')
    senha = data.get('senha')
    genero = data.get('genero')

    if not all([nome_usuario, email, senha, genero]):
        return jsonify({"status": "fail", "reason": "Campos faltando."}), 400
    
    if ' ' in nome_usuario:
        return jsonify({"status": "fail", "reason": "Nome de usuário não pode conter espaços."}), 400

    usuario_por_email = database.obter_usuario(email)
    usuario_por_nome = database.obter_usuario_por_nome(nome_usuario)

    if usuario_por_email:
        return jsonify({"status": "fail", "reason": "email already exists"}), 400
    if usuario_por_nome:
        return jsonify({"status": "fail", "reason": "username already exists"}), 400
    
    if len(senha) < 8 or not re.search(r'\d', senha) or ' ' in senha:
        return jsonify({"status": "fail", "reason": "Senha deve ter ao menos 8 caracteres, conter números e não ter espaços."}), 400

    token = secrets.token_hex(16)
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()
    database.salvar_usuario(nome_usuario, senha_hash, email, genero, token)

    corpo_email = f"""
        <p>Olá, {nome_usuario}</p>
        <p>Você fez um cadastro no Reciclapp. Para confirmar seu cadastro, valide sua conta em 15 minutos com este token:</p>
        <p><strong>{token}</strong></p>
        <p>* Mensagem automática, favor não responder.</p>
    """

    sucesso = bot_email.enviar_token(email, "Confirmação de Registro", corpo_email)
    return jsonify({"status": "success" if sucesso else "fail", "reason": "Erro ao enviar E-mail." if not sucesso else None}), 200 if sucesso else 500


@app.route('/verificar-token', methods=['POST'])
def verificar_token():
    data = request.json
    email = data.get('email')
    token = data.get('token')

    if not email or not token:
        return jsonify({"status": "fail", "reason": "E-mail ou token faltando."}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404

    if usuario['user_token'] != token:
        return jsonify({"status": "fail", "reason": "Token incorreto."}), 400

    created_at = usuario['created_at']
    if created_at and datetime.now() > created_at + timedelta(minutes=15):
        database.excluir_usuario(email)
        return jsonify({"status": "fail", "reason": "Token, expirado, usuário deletado."}), 400

    database.marcar_usuario_como_validado(email)

    return jsonify({"status": "success", "message": "Token verificado com sucesso!"}), 200


@app.route('/excluir-conta', methods=['POST'])
def excluir_conta():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"status": "fail", "reason": "E-mail faltando."}), 400

    usuario = database.obter_usuario(email)
    if usuario:
        database.excluir_usuario(email)
        return jsonify({"status": "success", "message": "Conta excluída com sucesso!"}), 200
    return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404


@app.route('/atualizar-senha', methods=['POST'])
def atualizar_senha():
    data = request.json
    email = data.get('email')
    nova_senha = data.get('nova_senha')

    if not all([email, nova_senha]):
        return jsonify({"status": "fail", "reason": "Campos faltando."}), 400

    if len(nova_senha) < 8 or not re.search(r'\d', nova_senha) or ' ' in nova_senha:
        return jsonify({"status": "fail", "reason": "Senha deve ter ao menos 8 caracteres, conter números e não ter espaços."}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404

    sucesso = database.atualizar_senha_por_email(email, nova_senha)
    return jsonify({"status": "Senha atualizada com SuCelso!" if sucesso else "fail"}), 200 if sucesso else 404


@app.route('/solicitar-recuperacao-senha', methods=['POST'])
def solicitar_recuperacao_senha():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"status": "fail", "reason": "E-mail falntando."}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404

    reset_token = secrets.token_hex(16)
    reset_token_expiration = datetime.now() + timedelta(minutes=15)
    database.definir_reset_token(email, reset_token, reset_token_expiration)

    mensagem = f"""
        <p>Olá,</p>
        <p>Você solicitou a recuperação de senha. Use o token abaixo para redefinir sua senha. Esse token é válido por 15 minutos.</p>
        <p><strong>{reset_token}</strong></p>
    """
    sucesso = bot_email.enviar_token(email, "Recuperação de Senha", mensagem)
    return jsonify({"status": "success" if sucesso else "fail", "reason": "Erro ao mandar E-mail." if not sucesso else None}), 200 if sucesso else 500


@app.route('/resetar-senha', methods=['POST'])
def resetar_senha():
    data = request.json
    email = data.get('email')
    reset_token = data.get('reset_token')
    nova_senha = data.get('nova_senha')

    if not all([email, reset_token, nova_senha]):
        return jsonify({"status": "fail", "reason": "Campos faltando."}), 400
    
    if len(nova_senha) < 8 or not re.search(r'\d', nova_senha) or ' ' in nova_senha:
        return jsonify({"status": "fail", "reason": "Senha deve ter ao menos 8 caracteres, conter números e não ter espaços."}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        print(f"Usuário não encontrado para o email: {email}")
        return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404

    if usuario.get('reset_token') != reset_token:
        print(f"Token inválido para o email: {email}")
        return jsonify({"status": "fail", "reason": "Token inválido ou expirado."}), 400

    if datetime.now() > usuario['reset_token_expiration']:
        print(f"Token expirado para o email: {email}")
        return jsonify({"status": "fail", "reason": "Token expirado."}), 400

    # Atualiza a senha
    sucesso = database.atualizar_senha_por_email(email, nova_senha)

    if sucesso:
        database.remover_reset_token(email)
        print(f"Senha atualizada com sucesso para o email: {email}")
        return jsonify({"status": "success", "message": "Senha redefinida com sucesso!"}), 200
    else:
        print(f"Falha ao atualizar senha para o email: {email}")
        return jsonify({"status": "fail", "reason": "Falha ao atualizar senha."}), 500


@app.route('/registrar-visualizacao', methods=['POST'])
def registrar_visualizacao():
    data = request.json
    email = data.get('email')
    enterprise_id = data.get('enterprise_id')

    if not all([email, enterprise_id]):
        return jsonify({"status": "fail", "reason": "Id da empresa está faltando."}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404

    users_id = usuario['id']
    database.salvar_visualizacao(users_id, enterprise_id)
    return jsonify({"status": "success", "message": "Visualização registrada com sucesso!"}), 200


@app.route('/obter-historico', methods=['POST'])
def obter_historico():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"status": "fail", "reason": "E-mail está faltando"}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404

    users_id = usuario['id']
    historico = database.obter_historico_usuario(users_id)

    return jsonify({"status": "success", "historico": historico}), 200


@app.route('/info-perfil', methods=['POST'])
def obter_perfil():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({"status": "fail", "reason": "E-mail está faltando."}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404

    return jsonify({
        "status": "success",
        "nome": usuario['username'],
        "genero": usuario['user_genero']
    }), 200


@app.route('/grafico', methods=['POST'])
def gerar_grafico_post():
    try:
        # Obter dados enviados no corpo da requisição
        data = request.json
        ano = data.get('ano')
        mes = data.get('mes')

        # Validação de entrada
        if not ano or not mes:
            return jsonify({"status": "fail", "reason": "Ano ou mês estão faltando."}), 400

        # Importa o módulo correto com base no ano
        modulo_nome = f'graficos.graficos{ano}'
        print(f"Importando módulo: {modulo_nome}")
        modulo_graficos = importlib.import_module(modulo_nome)

        # Chama a função de geração de gráfico no módulo importado
        fig = modulo_graficos.gerar_grafico(mes)
        if fig is None:
            raise ValueError("A função gerar_grafico retornou None.")
        
        # Salva o gráfico em um buffer para envio como resposta
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)

        return send_file(buf, mimetype='image/png')

    except ModuleNotFoundError:
        return jsonify({"status": "fail", "reason": f"Módulo não encontrado para ano {ano}."}), 404
    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"status": "fail", "reason": str(e)}), 500
    

@app.route('/empresa', methods=['POST'])
def obter_empresa():
    data = request.json
    nome_empresa = data.get('nome_empresa')

    if not nome_empresa:
        return jsonify({"status": "fail", "reason": "Nome da empresa está faltando."}), 400

    try:
        # Timeout de 10 segundos
        empresa = run_with_timeout(database.obter_empresa_por_nome, 10, nome_empresa)
        if not empresa:
            return jsonify({"status": "fail", "reason": "Empresa não encontrada."}), 404

        return jsonify({"status": "success", "empresa": empresa}), 200
    except TimeoutException:
        return jsonify({"status": "fail", "reason": "Tempo limite atingido"}), 504
    except Exception as e:
        print(f"Erro: {str(e)}")
        return jsonify({"status": "fail", "reason": "Erro interno no servidor"}), 500 
    

@app.route('/listar-empresas', methods=['POST'])

def listar_empresas():
    data = request.json
    email = data.get('email')
    user_lat = data.get('latitude')
    user_lng = data.get('longitude')

    if not all([email, user_lat, user_lng]):
        return jsonify({"status": "fail", "reason": "Latitude ou longitude faltando."}), 400

    usuario = database.obter_usuario(email)
    if not usuario:
        return jsonify({"status": "fail", "reason": "Usuário não encontrado."}), 404

    empresas = database.obter_empresas()

    
    empresas_distancia = []
    for empresa in empresas:
        distancia = calcular_distancia(float(user_lat), float(user_lng), empresa['latitude'], empresa['longitude'])
        empresas_distancia.append({
            "id": empresa['id'],
            "nome": empresa['nome'],
            "distancia_km": round(distancia, 2)
        })

    empresas_distancia.sort(key=lambda x: x['distancia_km'])

    return jsonify({"status": "success", "empresas": empresas_distancia}), 200

if __name__ == '__main__':
    app.run(port=5000)