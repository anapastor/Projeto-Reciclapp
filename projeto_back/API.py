from flask import Flask, request, jsonify
import bot_email
import secrets
import database
import secrets
import hashlib

app = Flask(__name__)
database.criar_tabela()

@app.route('/enviar-email', methods=['POST'])
def enviar_email():
    data = request.json
    nome_usuario = data.get('nome_usuario')
    email = data.get('email')
    senha = data.get('senha')
    genero = data.get('genero')

    if not all([nome_usuario, email, senha, genero]):
        return jsonify({"status": "fail", "reason": "missing fields"}), 400

    
    token = secrets.token_hex(16)

    senha_hash = hashlib.sha256(senha.encode()).hexdigest()


    database.salvar_usuario(nome_usuario, senha_hash, email, genero, token)

    corpo_email = f"""
        <p>Olá, {nome_usuario}</p>
        <p>Você fez um cadastro no Reciclapp. Para confirmar seu cadastro, valide sua conta com este token:</p>
        <p><strong>{token}</strong></p>
        <p>Este procedimento é necessário para sua segurança e o melhor funcionamento do aplicativo.</p>
        <p>* Mensagem automática, favor não responder.</p>
    """

    sucesso = envio_email.enviar_token(email, "Confirmação de Registro", corpo_email)
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

    if database.verificar_token(email, token):
        return jsonify({"status": "success", "message": "Token verificado com sucesso!"}), 200
    else:
        return jsonify({"status": "fail", "reason": "token incorrect or expired"}), 400

if __name__ == '__main__':
    app.run(port=5000)