import smtplib
from email.mime.text import MIMEText

def send_mail(name, email, phone, message):
    port = 2525
    smtp_server = 'smtp.mailtrap.io'
    login = '358124e4561b2c'
    password = '5b7f1f3d64c62d'
    message = f"<h3>New Contact message submission</h3><ul><li>Name: {name}</li><li>Email: {email}</li><li>Phone: {phone}</li><li>Message: {message}</li></ul>"

    sender_email = 'email1@example.com'
    reciever_email = 'email2@example.com'
    message = MIMEText(message, 'html')
    message['Subject'] = 'Urban Winner Contact'
    message['From'] = sender_email
    message['To'] = reciever_email

    # send email
    with smtplib.SMTP(smtp_server, port) as server:
        server.login(login, password)
        server.sendmail(sender_email, reciever_email, message.as_string())
