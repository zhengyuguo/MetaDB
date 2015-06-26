from flask.ext.mail import Message
from __init__ import *
from flask import render_template

app.config.update(
    MAIL_USE_SSL= True,
    MAIL_USE_TLS=False, 
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USERNAME= 'Your Gmail User Name',
    MAIL_PASSWORD='Your Gmail Password'
)
ADMINS = ['Your Gmail Address']

mail = Mail(app)

def send_email(subject, sender, recipients, html_body):
	msg = Message(subject, sender = sender, recipients = recipients)
	msg.body = "This is the email body"
	msg.html = html_body
	mail.send(msg)


def send_notification_email(newUser):
	send_email("[RNASeqMetaDB] Hi, %s, welcom you!" % newUser.name,
 				ADMINS[0],
 				[newUser.email],
				render_template("email.html"))

def send_email_test():
	msg = Message(
        'Hello',
        sender='qiaowei8993@gmail.com',
        recipients=
        ['qiaowei8993@gmail.com'])
	msg.body = "This is the email body"
	mail.send(msg)
	return "Sent"
