#Soneka, eu instalei muitas Bibliotecas, n sei se vai rodar direto
import pyodbc #Biblioteca para o CRUD.
import hashlib #Biblioteca para criptografar a senha.

# String de conexão corrigida para MySQL(O meu, o teu provavelmente nao tem senha).
dados_conexao = (
    "DRIVER={MySQL ODBC 9.0 ANSI Driver};"
    "SERVER=localhost;"
    "DATABASE=reciclapp;"
    "USER=root;"
    "PASSWORD=12345678;"
    "PORT: 3306;"
)

conexao = pyodbc.connect(dados_conexao) #Garantir a conexão e testá-la.
cursor = conexao.cursor() #Elemento que executa os comandos SQL do Python.


#Deicei Assim pq sou HORRIVEL com POO
#class User():                      #Construtor que torna dinâmico a passagem de parâmetros
#    def __init__(self, username, password, email) -> None:
#       self.username = username
#       self.password = password
#        self.email = email



def login(user_input, password):
    query = """
            SELECT * FROM users
            WHERE (username = ? OR user_email = ?) AND user_password = SHA2(?, 256);
            """
    cursor.execute(query, (user_input, user_input, password))
    result = cursor.fetchone()

    if result:
        print("Login bem-sucedido! Bem-vindo(a),", result[1])
    else:
        print("Erro: Usuário/email não encontrado ou senha inválida.")


def registro(username, user_password, user_email, user_genero):
    user_password_hash = hashlib.sha256(user_password.encode()).hexdigest()

    registrar = """insert into users(username, user_password, user_email, user_genero)
    values(?, ?, ?, ?)"""     #Comando do MySQL.

    cursor.execute(registrar, (username, user_password_hash, user_email, user_genero))  #Executa o comando dado.
    cursor.commit()  #Esse comando atualiza tudo que você edita no seu banco de dados.,




username = input("Digite sua nametag: ")
user_email = input("Digite seu email: ")
user_password = input("Digite sua senha: ")
user_genero = input("Digite seu genero: ")
registro(username, user_password, user_email, user_genero)
