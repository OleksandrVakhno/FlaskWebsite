from email.mime.text import MIMEText
from smtplib import SMTP

def send_email(email, height, average, count):
    from_email = "vakhno.alex@gmail.com"
    from_password = "12345678Va!"
    to_email=email

    subject="Height data"
    message ="Your height is <strong>%s</strong>. <br> Average height out of <strong>%s</strong> website users is <strong>%s</strong>.<br>" %(height, count, average)

    mail = MIMEText(message, 'html')
    mail['Subject']= subject
    mail['To']= to_email
    mail['From']=from_email

    gmail = SMTP('smtp.gmail.com', 587)
    gmail.ehlo()
    gmail.starttls()
    gmail.login(from_email,from_password)
    gmail.send_message(mail)