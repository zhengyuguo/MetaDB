# vim: set noexpandtab tabstop=2:
from flask.ext.mail import Message
from flask import Flask, render_template
from flask.ext.mail import Mail

app = Flask(__name__)
app.config.update(
    MAIL_USE_SSL= True,
    MAIL_USE_TLS=False, 
    MAIL_SERVER='smtp.gmail.com',
    MAIL_PORT=465,
    MAIL_USERNAME= 'rnaseqmetadb@gmail.com',
    MAIL_PASSWORD='YULABmetadb'
)

mail = Mail(app)

ADMINS = ['rnaseqmetadb@gmail.com']
def send_email(subject, sender, recipients, html_body):
	msg = Message(subject, sender = sender, recipients = recipients)
	msg.body = "This is the email body"
	msg.html = html_body
	mail.send(msg)


def send_notification_email(name, email, randomcode):
	send_email("[RNASeqMetaDB] Hi, %s, welcom you!" % name,
 				ADMINS[0],
 				[email],
				render_template("email.html", name = name, email = email, randomcode = randomcode ))

