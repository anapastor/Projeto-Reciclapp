import pyodbc
import hashlib

dados_conexao = (
    "DRIVER={MySQL ODBC 9.0 ANSI Driver};"
    "SERVER=localhost;"
    "DATABASE=reciclapp;"
    "USER=root;"
    "PASSWORD=12345678;"
    "PORT=3306;"
)
conexao = pyodbc.connect(dados_conexao)
cursor = conexao.cursor()

def salvar_usuario(username, user_password, user_email, user_genero, user_token):
    cursor.execute('''
        REPLACE INTO users(username, user_password, user_email, user_genero, user_token)
        VALUES (?, ?, ?, ?, ?)
    ''', (username, user_password, user_email, user_genero, user_token))
    conexao.commit()


def verificar_token(email, token):
    cursor.execute('SELECT token FROM usuarios WHERE email = ?', (email,))
    resultado = cursor.fetchone()
    return resultado and resultado[0] == token