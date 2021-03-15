import json
import lxml
import smtplib
import requests

from bs4 import BeautifulSoup

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
	mail["From"] = "Ígéretfigyelő kapcsolat"
	mail["To"] = "gergely.tomanovics@gmail.com"

	part1 = MIMEText(body["text"], 'plain')
	part2 = MIMEText(body["html"], 'html')

	mail.attach(part1)
	mail.attach(part2)

	server.sendmail(sent_from, to, mail.as_string())
	server.close()


def sql_injection_filter(string):

	try:
	
		if string.find("DROP") != -1:
			return "error_suspicious_string"
		elif string.find("1=1") != -1 or string.find("1 = 1") != -1:
			return "error_suspicious_string"
		elif ";" in string:
			return "error_suspicious_string"
		else:
			return string

	except:
		return None


class ScrapeEasy:

	def __init__(self, url):
		
		try:
			self.response = requests.get(url)

			print(self.response.status_code)

			if self.response.status_code == 200:
				self.response_error = False

				self.soup = BeautifulSoup(self.response.content, "lxml")
				self.meta_tags_to_dict()
			else:
				self.response_error = True
		except:
			self.response_error = True

	def meta_tags_to_dict(self):
		self.meta_dict = dict()
		meta_tags = self.soup.find_all("meta")
		for mt in meta_tags:
			try:
				self.meta_dict[mt.get("name")] = {"property" : mt.get("property"), "content" : mt.get("content")}
			except:
				print("Fail:", mt)
				self.meta_dict[mt.get("name")] = {"property" : mt.get("property"), "content" : mt.get("content")}