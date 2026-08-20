import smtplib
from email.mime.text import MIMEText

SMTP_HOST = '127.0.0.1'
SMTP_PORT = 1025
FROM_EMAIL = 'admin@parking'

def send_mail(to, subject, body, html = False):
    msg = MIMEText(body, 'html' if html else 'plain')
    msg['Subject'] = subject
    msg['From'] = FROM_EMAIL
    msg['To'] = to

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.send_message(msg)