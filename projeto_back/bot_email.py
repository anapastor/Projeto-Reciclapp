import win32com.client as win32

try:
    outlook = win32.Dispatch('outlook.application')
    email = outlook.CreateItem(0)
    email.To = "guilhermekalleu@gmail.com"
    email.Subject = "Cadastro no Reciclapp"
    email.HTMLBody = """
    <p>Olá "Usuario",</p>
    <p>Você fez um cadastro no Reciclapp. Para confirmar seu cadastro você deve validar sua conta com este token.</p>
    <p>Este procedimento é necessário para sua segurança e o melhor funcionamento do aplicativo.</p>
    <p>Token para validação: token</p>
    <p>Agora como membro registrado você tem um login exclusivo e acesso total as funcionalidades do app, pode usar!</p>
    <p>* Mensagem automática, favor não responder.</p>
    """
    email.Send()
    print("Email enviado com sucesso!")
except Exception as e:
    print(f"Ocorreu um erro: {e}")