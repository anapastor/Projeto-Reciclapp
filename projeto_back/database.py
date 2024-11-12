import pyodbc
import hashlib
import datetime

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
    created_at = datetime.datetime.now()
    cursor.execute('''
        REPLACE INTO users(username, user_password, user_email, user_genero, user_token, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (username, user_password, user_email, user_genero, user_token, created_at))
    conexao.commit()

def excluir_usuario(email):
    cursor.execute('DELETE FROM users WHERE user_email = ?', (email,))
    conexao.commit()

def obter_usuario(email):
    cursor.execute('SELECT username, user_password, user_email, user_genero, user_token, created_at FROM users WHERE user_email = ?', (email,))
    resultado = cursor.fetchone()
    if resultado:
        return {
            'username': resultado[0],
            'user_password': resultado[1],
            'user_email': resultado[2],
            'user_genero': resultado[3],
            'user_token': resultado[4],
            'created_at': resultado[5]
        }
    return None

def obter_email_do_token(token):
    cursor.execute('SELECT user_email FROM users WHERE user_token = ?', (token,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def verificar_token(email, token):
    cursor.execute('SELECT user_token FROM users WHERE user_email = ?', (email,))
    resultado = cursor.fetchone()
    return resultado and resultado[0] == token