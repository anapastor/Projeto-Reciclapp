import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import email.message

def enviar_token(destinatario, assunto, mensagem):

    smtp_server =  "smtp.gmail.com"
    smtp_port = 587
    remetente = "reciclappinc@gmail.com"
    senha = "eapt dtpl vjjy ctce"

    msg =  MIMEMultipart()
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
        server.quit