from socket import *
import ssl
import base64
import getpass
import mimetypes
import os

mailserver = ("smtp.gmail.com", 587) 
USAR_TLS = True  
USUARIO = "celiaslongoraizer@gmail.com" #email autorizado para solicitar o envio da mensagem
REMETENTE = "celiaslongoraizer@gmail.com"     
DESTINATARIO = "celia.cristina.slongo.raizer@gmail.com"
ASSUNTO = "Lab 3 - SMTP com TLS"
#CAMINHO_IMAGEM = None                         
CAMINHO_IMAGEM = "imagem.jpg"                 
 
msg = "\r\n Eu amo redes de computadores!"
endmsg = "\r\n.\r\n"

# Função para enviar comandos SMTP 
def comando(sock, cmd, esperado, mostrar=None): 
    """Envia um comando SMTP, imprime a resposta e confere o código esperado."""
    print("C:", mostrar if mostrar is not None else cmd) 
    sock.send((cmd + "\r\n").encode()) 
    resp = sock.recv(4096).decode() 
    print("S:", resp)
    if resp[:3] != esperado: 
        print(f"{esperado} resposta não recebida do servidor.")
    return resp
 
clientSocket = socket(AF_INET, SOCK_STREAM) #socket TCP
clientSocket.connect(mailserver) 

#220 - servidor está pronto para iniciar a comunicação.
recv = clientSocket.recv(1024).decode()
print(recv)

if recv[:3] != '220':
    print('220 resposta não recebida do servidor.')
 

if USAR_TLS or USUARIO:
    comando(clientSocket, "EHLO Alice", "250")
else:
    comando(clientSocket, "HELO Alice", "250")
 

if USAR_TLS:#verifica se tls true
    comando(clientSocket, "STARTTLS", "220") 
    contexto = ssl.create_default_context()
    clientSocket = contexto.wrap_socket(clientSocket, server_hostname=mailserver[0]) 
    comando(clientSocket, "EHLO Alice", "250")      
 

if USUARIO:
    senha = getpass.getpass("Senha (senha de app no Gmail): ")
    comando(clientSocket, "AUTH LOGIN", "334") #inicia a autenticação
    comando(clientSocket, base64.b64encode(USUARIO.encode()).decode(), "334") #solicita e envia client codificado
    comando(clientSocket, base64.b64encode(senha.encode()).decode(), "235", # solicita envia senha codificada
            mostrar="<senha em base64>")
 

comando(clientSocket, f"MAIL FROM:<{REMETENTE}>", "250") 
comando(clientSocket, f"RCPT TO:<{DESTINATARIO}>", "250")
comando(clientSocket, "DATA", "354") 
 
cabecalhos = (f"From: {REMETENTE}\r\n"
              f"To: {DESTINATARIO}\r\n"
              f"Subject: {ASSUNTO}\r\n")


if CAMINHO_IMAGEM is None:
    # Mensagem simples, só texto
    clientSocket.send(cabecalhos.encode())
    clientSocket.send(msg.encode())
else:
    # --- Opcional 2: MIME multipart (texto + imagem) ---
    fronteira = "==LAB3_SMTP_BOUNDARY=="
    nome = os.path.basename(CAMINHO_IMAGEM)
    tipo = mimetypes.guess_type(CAMINHO_IMAGEM)[0] or "application/octet-stream"
    with open(CAMINHO_IMAGEM, "rb") as f:
        img_b64 = base64.encodebytes(f.read()).decode().replace("\n", "\r\n")
 
    mensagem = (
        cabecalhos +
        "MIME-Version: 1.0\r\n"
        f'Content-Type: multipart/mixed; boundary="{fronteira}"\r\n'
        "\r\n"
        f"--{fronteira}\r\n"
        "Content-Type: text/plain; charset=utf-8\r\n"
        "Content-Transfer-Encoding: 8bit\r\n"
        f"{msg}\r\n"
        f"--{fronteira}\r\n"
        f'Content-Type: {tipo}; name="{nome}"\r\n'
        "Content-Transfer-Encoding: base64\r\n"
        f'Content-Disposition: attachment; filename="{nome}"\r\n'
        "\r\n"
        f"{img_b64}\r\n"
        f"--{fronteira}--"
    )
    clientSocket.send(mensagem.encode("utf-8"))


clientSocket.send(endmsg.encode())  #fim do conteudo do email
recv5 = clientSocket.recv(1024).decode() #recebe a resposta do servidor
print(recv5)
if recv5[:3] != '250': #se a resposta for diferente de 250, significa que houve algum erro no envio do e-mail
    print('250 resposta não recebida do servidor.') 
 
# encerra a seção
comando(clientSocket, "QUIT", "221") 
clientSocket.close()


 # ehkk tyke pypc caez
