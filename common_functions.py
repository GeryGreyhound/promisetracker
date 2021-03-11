import json
import smtplib

from email.mime.text import MIMEText as text
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(subject, body, extra_options = dict()):
	with open("email.conf") as config_file:
		config = json.loads(config_file.read())

	server = smtplib.SMTP_SSL(config['smtp_server'], config['smtp_port'])

	email_username = config["username"]
	email_password = config["password"]
	server.login(email_username, email_password)
	sent_from = config["sent_from"]
	
	if not "email_list" in extra_options:
		to = "gergely.tomanovics@gmail.com"
	else:
		to = extra_options["email_list"]

	# mail = text(body)
	mail = MIMEMultipart('alternative')

	mail["Subject"] = subject
	mail["From"] = "Ígéretfigyelő"
	mail["To"] = "gergely.tomanovics@gmail.com"

	part1 = MIMEText(body["text"], 'plain')
	part2 = MIMEText(body["html"], 'html')

	mail.attach(part1)
	mail.attach(part2)

	server.sendmail(sent_from, to, mail.as_string())
	server.close()