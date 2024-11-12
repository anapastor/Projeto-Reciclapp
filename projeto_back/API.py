from flask import Flask, request, jsonify
import bot_email
import secrets
import database
import hashlib
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta


def excluir_usuarios_expirados():
    # Consulta os usuários com o token e a data de criação
    cursor = database.conexao.cursor()
    cursor.execute("SELECT user_email, created_at FROM users")
    usuarios = cursor.fetchall()

    for usuario in usuarios:
        email, created_at = usuario
        if created_at:
            # Verifica se o token expirou (15 minutos)
            if datetime.now() > created_at + timedelta(minutes=2):
                database.excluir_usuario(email)
                print(f"Usuário {email} excluído por expiração do token.")

# Configurar o agendador
scheduler = BackgroundScheduler()
scheduler.add_job(excluir_usuarios_expirados, 'interval', minutes=1)  # Executa a cada 1 minuto
scheduler.start()

app = Flask(__name__)

@app.route('/enviar-email', methods=['POST'])
def enviar_email():
    data = request.json
    nome_usuario = data.get('nome_usuario')
    email = data.get('email')
    senha = data.get('senha')
    genero = data.get('genero')

    if not all([nome_usuario, email, senha, genero]):
        return jsonify({"status": "fail", "reason": "missing fields"}), 400

    # Gera um token de verificação
    token = secrets.token_hex(16)

    # Criptografa a senha
    senha_hash = hashlib.sha256(senha.encode()).hexdigest()

    # Salva o usuário no banco de dados
    database.salvar_usuario(nome_usuario, senha_hash, email, genero, token)

    # Corpo do e-mail de verificação
    corpo_email = f"""
        <p>Olá, {nome_usuario}</p>
        <p>Você fez um cadastro no Reciclapp. Para confirmar seu cadastro, valide sua conta em 15 minutos com este token:</p>
        <p><strong>{token}</strong></p>
        <p>Este procedimento é necessário para sua segurança e o melhor funcionamento do aplicativo.</p>
        <p>* Mensagem automática, favor não responder.</p>
    """

    # Envia o e-mail com o token
    sucesso = bot_email.enviar_token(email, "Confirmação de Registro", corpo_email)
    if sucesso:
        return jsonify({"status": "success"}), 200
    else:
        return jsonify({"status": "fail", "reason": "error sending email"}), 500



@app.route('/verificar-token', methods=['POST'])
def verificar_token():
    data = request.json
    email = data.get('email')
    token = data.get('token')

    if not email or not token:
        return jsonify({"status": "fail", "reason": "email or token missing"}), 400

    # Obtém o usuário do banco de dados
    usuario = database.obter_usuario(email)

    if not usuario:
        return jsonify({"status": "fail", "reason": "user not found"}), 404

    # Verifica se o token está correto
    if usuario['user_token'] != token:
        return jsonify({"status": "fail", "reason": "token incorrect"}), 400

    # Verifica se o token expirou (considerando que o token tem 15 minutos de validade)
    created_at = usuario['created_at']
    if created_at:
        data_criacao = created_at
        if datetime.now() > data_criacao + timedelta(minutes=2):
            # Exclui o usuário se o token expirou
            database.excluir_usuario(email)
            return jsonify({"status": "fail", "reason": "token expired, user deleted"}), 400

    return jsonify({"status": "success", "message": "Token verificado com sucesso!"}), 200



@app.route('/excluir-conta', methods=['POST'])
def excluir_conta():
    data = request.json
    token = data.get('token')

    if not token:
        return jsonify({"status": "fail", "reason": "token missing"}), 400

    # Obtenha o email usando o token do usuário
    email = database.obter_email_do_token(token)
    
    if email:
        # Exclua o usuário com o email obtido
        database.excluir_usuario(email)
        return jsonify({"status": "success", "message": "Conta excluída com sucesso!"}), 200
    else:
        return jsonify({"status": "fail", "reason": "usuário não encontrado"}), 404


if __name__ == '__main__':
    app.run(port=5000)