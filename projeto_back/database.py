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
    cursor.execute('DELETE FROM company_history WHERE users_id = (SELECT id FROM users WHERE user_email = ?)', (email,))
    conexao.commit()

    # Agora, excluir o usuário
    cursor.execute('DELETE FROM users WHERE user_email = ?', (email,))
    conexao.commit()

def obter_usuario(email):
    cursor.execute('SELECT * FROM users WHERE user_email = ?', (email,))
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def obter_usuario_por_nome(username):
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    row = cursor.fetchone()
    if row:
        columns = [column[0] for column in cursor.description]
        return dict(zip(columns, row))
    return None

def obter_email_do_token(token):
    cursor.execute('SELECT user_email FROM users WHERE user_token = ?', (token,))
    resultado = cursor.fetchone()
    return resultado[0] if resultado else None

def verificar_token(email, token):
    cursor.execute('SELECT user_token FROM users WHERE user_email = ?', (email,))
    resultado = cursor.fetchone()
    return resultado and resultado[0] == token

def atualizar_senha(user_token, nova_senha):
    senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
    cursor.execute('''
        UPDATE users
        SET user_password = ?
        WHERE user_token = ?
    ''', (senha_hash, user_token))
    conexao.commit()
    return cursor.rowcount > 0

def atualizar_senha_por_email(email, nova_senha):
    senha_hash = hashlib.sha256(nova_senha.encode()).hexdigest()
    cursor.execute('''
        UPDATE users
        SET user_password = ?
        WHERE user_email = ?
    ''', (senha_hash, email))
    conexao.commit()

    if cursor.rowcount > 0:
        return True
    return False

def definir_reset_token(email, reset_token, reset_token_expiration):
    cursor.execute('''
        UPDATE users SET reset_token = ?, reset_token_expiration = ?
        WHERE user_email = ?
    ''', (reset_token, reset_token_expiration, email))
    conexao.commit()

def remover_reset_token(email):
    cursor.execute('''
        UPDATE users SET reset_token = NULL, reset_token_expiration = NULL
        WHERE user_email = ?
    ''', (email,))
    conexao.commit()

def marcar_usuario_como_validado(email):
    cursor.execute('''
        UPDATE users
        SET is_validated = TRUE
        WHERE user_email = ?
    ''', (email,))
    conexao.commit()

def salvar_visualizacao(users_id, enterprise_id):
    data_visualizacao = datetime.datetime.now()
    cursor.execute('''
        INSERT INTO company_history (users_id, enterprise_id, data_visualizacao)
        VALUES (?, ?, ?)
    ''', (users_id, enterprise_id, data_visualizacao))
    conexao.commit()

def obter_historico_usuario(users_id):
    query = '''
        SELECT ch.id, ch.data_visualizacao, c.nome, c.endereco, c.bairro, c.cep, c.telefone, c.email, 
               c.latitude, c.longitude, c.descricao, c.foto
        FROM company_history ch
        JOIN companys c ON ch.enterprise_id = c.id
        WHERE ch.users_id = ?
        ORDER BY ch.data_visualizacao DESC
        LIMIT 10
    '''
    cursor.execute(query, (users_id,))
    rows = cursor.fetchall()
    
    historico = []
    for row in rows:
        historico.append({
            "id": row[0],
            "data_visualizacao": row[1],
            "nome": row[2],
            "endereco": row[3],
            "bairro": row[4],
            "cep": row[5],
            "telefone": row[6],
            "email": row[7],
            "latitude": row[8],
            "longitude": row[9],
            "descricao": row[10],
            "foto": row[11]
        })
    
    return historico

def obter_empresas():
    cursor.execute('SELECT id, nome, latitude, longitude FROM companys')
    rows = cursor.fetchall()
    empresas = []
    for row in rows:
        empresas.append({
            'id': row[0],
            'nome': row[1],
            'latitude': row[2],
            'longitude': row[3]
        })
    return empresas

def obter_empresa_por_nome(nome):
    try:
        query = '''
            SELECT id, nome, endereco, bairro, cep, telefone, email, latitude, longitude, descricao, foto
            FROM companys
            WHERE nome = ?
        '''
        print(f"Executando consulta: {query} com nome = {nome}")
        cursor.execute(query, (nome,))
        row = cursor.fetchone()
        if row:
            print(f"Resultado encontrado: {row}")
            return {
                "id": row[0],
                "nome": row[1],
                "endereco": row[2],
                "bairro": row[3],
                "cep": row[4],
                "telefone": row[5],
                "email": row[6],
                "latitude": row[7],
                "longitude": row[8],
                "descricao": row[9],
                "foto": row[10],
            }
        print("Nenhum resultado encontrado.")
        return None
    except Exception as e:
        print(f"Erro na consulta SQL: {e}")
        raise