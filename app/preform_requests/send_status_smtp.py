import configparser
import smtplib
from email.mime.text import MIMEText
from email.header import Header
# custom modules
import os
import sys
# script will be run fro /app directory
sys.path.append(os.path.abspath(os.getcwd()))  # adding app directory to path


def send(subject: str, mail_text: str = None):
    config = configparser.ConfigParser()
    config.read('../creds/passwords.ini', encoding='utf8')
    auth = ('uryyakir@gmail.com', config["gmail"]["password"])

    # Establish a secure session with gmail's outgoing SMTP server using your gmail account
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.login(auth[0], auth[1])

    if mail_text:
        msg = MIMEText(mail_text, _charset="UTF-8")

    else:
        msg = MIMEText('', _charset="UTF-8")

    msg['Subject'] = Header(subject, "utf-8")
    # Send text message through SMS gateway of destination number
    server.sendmail(auth[0], auth[0], msg.as_string())
