import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from supabase import create_client, Client

# Configurações do Supabase
SUPABASE_URL = "https://xykcdgzzuyjveulybftm.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inh5a2NkZ3p6dXlqdmV1bHliZnRtIiwicm9sZSI6ImFub24iLCJpYXQiOjE3MzA4NDMxNDUsImV4cCI6MjA0NjQxOTE0NX0.p0LzzuNLGZMIP-vT1EH--NPU6uoA2Xky44Nse31CtPA"
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# Função para gerar o token do Supabase
def gerar_token():
    try:
        response = supabase.rpc("generate_numeric_token").execute()
        if response.status_code == 200:
            token = response.data
            return token
        else:
            print("Erro ao gerar token:", response.json())
            return None
    except Exception as e:
        print("Erro na chamada RPC:", e)
        return None

# Função de envio de e-mail
def enviar_token(destinatario, assunto, token):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587
    remetente = "reciclappinc@gmail.com"
    senha = "eapt dtpl vjjy ctce"

    # Cria o conteúdo do e-mail com o token
    mensagem = f"""
    <html>
        <body>
            <p>Olá!</p>
            <p>Você fez um cadastro no Reciclapp. Para confirmar seu cadastro, valide sua conta com este token:</p>
            <p><strong>{token}</strong></p>
            <p>Este procedimento é necessário para sua segurança e o melhor funcionamento do aplicativo.</p>
            <p>* Mensagem automática, favor não responder.</p>
        </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto

    msg.attach(MIMEText(mensagem, 'html'))

    try:
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()
        server.login(remetente, senha)
        server.sendmail(remetente, destinatario, msg.as_string())
        print("Email enviado com sucesso!")

    except Exception as e:
        print(f"Erro ao enviar email: {e}")

    finally:
        server.quit()

# Função principal para gerar o token e enviar o e-mail
def gerar_e_enviar_email(destinatario):
    token = gerar_token()
    if token:
        enviar_token(destinatario, "Seu Código de Verificação", token)
    else:
        print("Não foi possível gerar o token.")

# Exemplo de uso
gerar_e_enviar_email("email_do_usuario@exemplo.com")