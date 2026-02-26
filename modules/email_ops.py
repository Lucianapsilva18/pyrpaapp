"""Módulo de operações de e-mail para o PyRPA."""

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders


class EmailOperations:

    def send_email(self, host, port, user, password, recipients, subject, body, attachment=None) -> dict:
        try:
            msg = MIMEMultipart()
            msg["From"] = user
            msg["To"] = ", ".join(recipients)
            msg["Subject"] = subject
            msg.attach(MIMEText(body, "plain", "utf-8"))

            if attachment:
                part = MIMEBase("application", "octet-stream")
                part.set_payload(attachment.read())
                encoders.encode_base64(part)
                part.add_header("Content-Disposition", f"attachment; filename={attachment.name}")
                msg.attach(part)

            with smtplib.SMTP(host, port) as server:
                server.starttls()
                server.login(user, password)
                server.sendmail(user, recipients, msg.as_string())

            return {"status": "Sucesso", "message": f"E-mail enviado para {', '.join(recipients)}"}
        except Exception as e:
            return {"status": "Erro", "message": str(e)}

    def generate_script(self, use_tls: bool = True, use_template: bool = False) -> str:
        if use_template:
            return '''"""
Script de envio de e-mail em lote com template gerado pelo PyRPA.
"""
import smtplib
import csv
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ── Configuração SMTP ──
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "seu_email@gmail.com"
SMTP_PASS = "sua_senha_de_app"      # Use App Password do Google

# ── Template ──
TEMPLATE = """
Olá {nome},

Segue o relatório referente ao mês de {mes} para a empresa {empresa}.

Atenciosamente,
Equipe de Automação
"""

ASSUNTO = "Relatório Mensal - {mes}"

def enviar_lote(csv_contatos: str, mes: str):
    """Envia e-mails em lote a partir de um CSV."""
    with open(csv_contatos, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        contatos = list(reader)

    print(f"Enviando para {len(contatos)} contato(s)...")

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASS)

        for contato in contatos:
            corpo = TEMPLATE.format(mes=mes, **contato)
            assunto = ASSUNTO.format(mes=mes)

            msg = MIMEMultipart()
            msg["From"] = SMTP_USER
            msg["To"] = contato["email"]
            msg["Subject"] = assunto
            msg.attach(MIMEText(corpo, "plain", "utf-8"))

            server.sendmail(SMTP_USER, contato["email"], msg.as_string())
            print(f"  ✓ Enviado para {contato['email']}")
            time.sleep(1)  # Respeitar rate limits

    print("Envio concluído!")

if __name__ == "__main__":
    # CSV deve ter colunas: email, nome, empresa
    enviar_lote("contatos.csv", "Janeiro/2025")
'''
        else:
            tls_block = "        server.starttls()" if use_tls else "        # TLS desabilitado"
            return f'''"""
Script de envio de e-mail gerado pelo PyRPA.
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from pathlib import Path

# ── Configuração ──
SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587
SMTP_USER = "seu_email@gmail.com"
SMTP_PASS = "sua_senha_de_app"

def enviar_email(destinatario: str, assunto: str, corpo: str, anexo: str = None):
    """Envia um e-mail com anexo opcional."""
    msg = MIMEMultipart()
    msg["From"] = SMTP_USER
    msg["To"] = destinatario
    msg["Subject"] = assunto
    msg.attach(MIMEText(corpo, "plain", "utf-8"))

    if anexo:
        path = Path(anexo)
        with open(path, "rb") as f:
            part = MIMEBase("application", "octet-stream")
            part.set_payload(f.read())
            encoders.encode_base64(part)
            part.add_header("Content-Disposition", f"attachment; filename={{path.name}}")
            msg.attach(part)

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
{tls_block}
        server.login(SMTP_USER, SMTP_PASS)
        server.sendmail(SMTP_USER, destinatario, msg.as_string())
        print(f"E-mail enviado para {{destinatario}}")

if __name__ == "__main__":
    enviar_email(
        destinatario="destino@email.com",
        assunto="Relatório Automatizado",
        corpo="Segue o relatório em anexo.",
        anexo="relatorio.pdf",
    )
'''
