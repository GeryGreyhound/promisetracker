
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
import psycopg2
from psycopg2.extensions import AsIs

import datetime
import requests

class DatabaseOperations:

	def __init__(self):
		config_file = "database.conf"

		with open(config_file) as config:
			db_config = config.read()
			
		self.connection = psycopg2.connect(db_config)
		self.connection.autocommit = True
		self.cursor = self.connection.cursor()

dbc = DatabaseOperations()

class Politician:
	def __init__(self, id):
		self.id = id
		self.get_basic_data()
		if self.existent:
			self.get_promise_list()

	def create_from_csv(self, csv_file):
		pass

	def get_basic_data(self):
		query_string = "SELECT * FROM politicians WHERE id = (%s)"
		query_data = [self.id]

		dbc.cursor.execute(query_string, query_data)
		self.basic_data = dbc.cursor.fetchone()

		if self.basic_data:
			self.existent = True
			self.name = self.basic_data[1]
			self.location = self.basic_data[2]
			self.position = self.basic_data[3]
			self.last_elected = self.basic_data[4]
			self.program_title = self.basic_data[5]
			self.first_elected = self.basic_data[6]

			if not self.last_elected:
				self.last_elected = self.elected

			dbc.cursor.execute("SELECT * FROM elections WHERE dt = (%s)", [self.first_elected])
			self.start_date = dbc.cursor.fetchone()[1]
			dbc.cursor.execute("SELECT * FROM elections WHERE id = (%s)", [self.last_elected])
			self.end_date = dbc.cursor.fetchone()[1]

		else:
			self.existent = False


	def get_promise_list(self):
		pass
		self.promise_list = PromiseList(self.id)
		# ehelyett a class PromiseList leg7yen inkább egy kölön class, és legyen egy self.promise_list ojjektum

	
		'''for category in promise_categories:
			category_details = dict()
			category_details["title"] = category[2]
			category_id = category[1]
			dbc.cursor.execute ("SELECT * FROM promises WHERE politician_id = %s AND category_id = %s AND (custom_options != 'draft' OR custom_options IS NULL) ORDER BY id", [politician, AsIs(str(category_id))])
			category_promises = dbc.cursor.fetchall()

			for promise in category_promises:
				promise_details = dict()

				promise_id = promise[0]
				promise_counter += 1
				dbc.cursor.execute ("SELECT * FROM news_articles WHERE politician_id = (%s) AND promise_id = (%s) ORDER BY article_date DESC", [self.id, promise_id])
		'''

class PromiseList:
	def __init__(self, politician_id):
		self.status_counters = {"promises" : 0, "success" : 0, "pending" : 0, "fail" : 0, "partly" : 0}
		self.politician_id = politician_id
		self.promise_list = list()

	def get_from_database(self):
		query_string = "SELECT * FROM promise_categories WHERE politician_id = (%s) ORDER BY category_id"
		query_data = [self.politician_id]

		dbc.cursor.execute(query_string, query_data)
		self.promise_categories = dbc.cursor.fetchall()

		for category in self.promise_categories:
			category_details = dict()
			category_id = category[1]
			category_details["title"] = category[2]

			promises_in_category = list()

			promises_query = "SELECT * FROM promises WHERE politician_id = %s AND category_id = %s AND (custom_options != 'draft' OR custom_options IS NULL) ORDER BY id",
			query_data = politician, [AsIs(str(category_id))]
			dbc.cursor.execute(promises_query, query_data)
			category_promises = dbc.cursor.fetchall()

			category_promises_list = list()

			for promise in category_promises:
				promise = Promise()
				self.status_counter["promises"] += 1

				promise.id = promise[0]
				promise.articles = list()

				query_string = "SELECT * FROM news_articles WHERE politician_id = (%s) AND promise_id =  (%s) ORDER BY article_date DESC"
				query_data = [politician_id, promise_id]
				dbc.cursor.execute(query_string, query_data)
				self.raw_data = dbc.cursor.fetchall()



				




class Promise:
	def __init__(self):
		# self.articles legyen az ígérethez kapcsolódó cikkek
		# mindegyik cikk is egy Article objektum, az Article class-ban lesz definiálva a létrejövése adatbázisból (Article.get_from_databased)
		pass

	def get_from_database(self, policitian_id, promise_id):
		pass

	def get_articles(self):
		pass

class Article:
	def __init__(self, url):
		print(url)
		self.url = url
		self.errors = list()

	def get_meta_data(self):

		if ".pdf" in self.url:
			r = requests.get(self.url)
			my_raw_data = r.content

			with open("my_pdf.pdf", 'wb') as my_data:
			    my_data.write(my_raw_data)
			
			open_pdf_file = open("my_pdf.pdf", 'rb')
			read_pdf = PdfFileReader(open_pdf_file)
			if read_pdf.isEncrypted:
			    read_pdf.decrypt("")

			info = read_pdf.getDocumentInfo()

			self.title = info.title
			if not self.title:
				self.errors.append("get_title_error")
			
			self.date = info["/CreationDate"]

			if self.date:
				try:
					self.date = datetime.datetime.strptime(self.date[2:10], "%Y%m%d")
				except:
					self.date = None
					self.errors.append("get_date_error")

			junk, url_base = self.url.split("//")
			url_base, junk = url_base.split("/", 1)
			
			self.source_name = url_base

		else:

			source_replaceable_url_parts = {"m.hvg.hu" : "hvg.hu"}
	
			title_replaceable_parts = {"Telex: ", ""}
	
			sources = {"facebook.com/133909266986" : "Facebook - VEKE",
					  "facebook.com/vekehu" : "Facebook - VEKE",
					  "facebook.com/karacsonygergely" : "Facebook - Karácsony Gergely",
					  "facebook.com/budapestmindenkie" : "Facebook - Budapest Városháza",
					  "index.hu" : "Index",
					  "telex.hu" : "Telex",
					  "444.hu" : "444",
					  "vastagbor.atlatszo" : "Vastagbőr blog"
					  }
	
			try:
				response = requests.get(self.url)
				if response.status_code != 200:
					self.errors.append("url_error")
			except:
				self.errors.append("url_error")	
	
			
			if not "url_error" in self.errors:
				soup = BeautifulSoup(response.text, "html.parser")
				metas = soup.find_all('meta')
	
				# A) try to get article title: 1: meta name = title, 2: meta property = og:title, 3: html <title> tag, 4: failed
	
				try: #1
					self.title = soup.find("meta",  attrs={'name':'title'})['content']
				except:
					try: #2
						self.title = soup.find("meta",  attrs={'property': 'og:title'})['content']
					except:
						try: #3
							self.title = soup.find("title").string
						except: #4
							self.title = None
							self.errors.append("get_title_error")
				
				# B) try to get date of the article: 1: meta property = article:published_time, 2: find date-like string in the URL (like YYYY/HH/MM), 3: failed
	
				try: #1
					self.date = soup.find("meta",  attrs={'property': 'article:published_time'})['content']
				except:
				
					try: #2
						url_parts = list(self.url.split("/"))
						for counter, part in enumerate(url_parts):
							if counter < len(url_parts) - 3:
								try:
									year, month, day = int(url_parts[counter]), int(url_parts[counter+1]), int(url_parts[counter+2])
									print("year, month, day",year, month, day)
									
									self.date = datetime.datetime(year, month, day).strftime("%Y-%m-%d")
	
								except:
									self.errors.append("get_date_error")
									self.date = '1982-01-18'
										
					except:
						self.errors.append("get_date_error")
						self.date = '1982-01-18' # needs to be stored in a timestamp column in the DB
	
				# C) try to get source name: 1: anything between http: //  and  / 2: Facebook page name via the predefined "sources" dict
				# Facebook: the html <title> is the page name
	
				junk, source_url = self.url.split("//")
				source_url, junk = source_url.split("/", 1)
				
				for x in source_replaceable_url_parts:
					source_url = source_url.replace(x, source_replaceable_url_parts[x])
				
				self.source_name = source_url
				
				for x in sources:
					if x in source_url:
						self.source_name = sources[x]
	
				for x in title_replaceable_parts:
					if x in self.title:
						self.title = self.title.replace("Telex: ", "")
				
				if "facebook" in self.url:
					title_string = soup.find("title").string
					title, junk = title_string.split(" - ")
					self.source_name = "Facebook - " + title
					self.article_title = None
					self.errors.append("get_title_error")

	def get_from_database(self):
		pass

	def add_to_submissions(self, politician_id, promise_id, submitter_name, submitter_ip, submit_date, suggested_status):

		dbc = DatabaseOperations()
		
		checkable_variables = [self.title, self.source_name, self.date]

		self.title = sql_injection_filter(self.title)
		self.source_name = sql_injection_filter(self.source_name)

		dbc.cursor.execute("SELECT id FROM submissions ORDER BY id DESC LIMIT 1")
		last_id = dbc.cursor.fetchone()[0]
		new_id = last_id + 1
		

		query_string = "INSERT INTO submissions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		query_data = [self.date, submitter_ip, self.url, self.source_name, self.title, politician_id, promise_id, submit_date, submitter_name, new_id, None, None, suggested_status]

		dbc.cursor.execute(query_string, query_data)


class Page:
	def __init__(self):
		self.defaults = {"language" : "hu", "google_analytics_id" : "UA-85693466-4", "facebook_page_id" : "igeretfigyelo", }

		try:
			if "language" in session:
				self.language = session["language"]
			else:
				self.language = self.defaults["language"]
		except:
			# no session mode for testing
			self.language = self.defaults["language"]

		# default values for page generator
		self.og_title = "Ígéretfigyelő - Promisetracker v2"
		self.og_description = "Ez itt a leírás"
		self.og_image = ""
		self.html_title = ""

	def construct_html(self):

		html_head = '''
		<!DOCTYPE html>
		<html lang="{}">
		<head>
		<script async src="https://www.googletagmanager.com/gtag/js?id={}"></script>
		<script>
  			window.dataLayer = window.dataLayer || [];
  			function gtag(){{dataLayer.push(arguments);}}
  			gtag('js', new Date());
  			gtag('config', '{}');
		</script>

		<script src='https://kit.fontawesome.com/a076d05399.js'></script>

		<meta charset="utf-8">
  		<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
 		<meta name="description" content="">
  		<meta name="author" content="">
  		<meta property="og:title" content="{}" />
  		<meta property="og:description" content="{}" />
  		<meta property="og:image" content="http://www.igeretfigyelo.hu/{}" />

  		<title>{}</title>

  		<!-- Bootstrap core CSS -->
  		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">

  		<!-- Custom styles for this template -->
  		<link href="/static/css/blog-home.css" rel="stylesheet">

  		</head>
		'''.format(self.language,
				   self.defaults["google_analytics_id"],
				   self.defaults["google_analytics_id"],
				   self.og_title,
				   self.og_description,
				   self.og_image,
				   self.html_title
				   )

		navbar = '''
		  <!-- Navigation -->
		  <nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
		  <div class="container">
		  <a class="navbar-brand" href="/">Ígéretfigyelő</a>
		  <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
		  <span class="navbar-toggler-icon"></span>
		  </button>
		
		  <div class="collapse navbar-collapse" id="navbarSupportedContent">
		    <ul class="navbar-nav mr-auto">
		      <li class="nav-item">
		        <a class="nav-link" href="/about">Mi ez és kik csinálják?</a>
		      </li>
		      <li class="nav-item dropdown">
		        <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
		          Politikusok
		        </a>
		        <div class="dropdown-menu" aria-labelledby="navbarDropdown">
		          <a class="dropdown-item" href="/csoziklaszlo">Csőzik László (Érd)</a>
		          <a class="dropdown-item" href="/fulopzsolt">Fülöp Zsolt (Szentendre)</a>
		          <a class="dropdown-item" href="/karacsonygergely">Karácsony Gergely (Budapest)</a>
		        </div>
		      </li>
		      <li class="nav-item">
		        <a class="nav-link" href="/contact">Kapcsolat</a>
		      </li>
		    </ul>
		  </div>
		</nav>
		'''

		self.html_page = html_head + "\n" + navbar






if __name__ == "__main__":

	f = request.form
	for key in f.keys():
		for value in f.getlist(key):
			print(key, value)
			print()
				
			try:
				v1,v2,permalink,promise_id = key.split("_")
			except:
				pass
			url = value

			try:
				response = requests.get(url)
			except:
				response = r_error()
				response.status_code = None
				
			print ("response.status_code", response.status_code)
				
			if not response.status_code:
				status_message["error"] = "A megadott URL (" + url + ") nem található, kérjük, ellenőrizd!"
				email_content = request.remote_addr + ',' + str(datetime.datetime.now()) + ',' + politician + ',' + promise_id + ',' + url
				# send_email("ÍgéretFigyelő: hibás cikkbeküldés", email_content)
	
			elif response.status_code == 200:

				soup = BeautifulSoup(response.text, "html.parser")
					
				article_title, published_date, source_name = fetch_article_data(url, soup)

				if "logged_in" in session:
					submitter_name = session["user_name"]
				else:
					submitter_name = "ismeretlen"

				status_message["success"] = "A cikk ('" + article_title + "') sikeresen beküldve!"
				status_message["details"] = dict()
				status_message["details"]["article_title"] = article_title
				status_message["details"]["submitter_name"] = submitter_name
				status_message["details"]["published_date"] = published_date
				status_message["details"]["source_name"] = source_name
				status_message["details"]["promise_id"] = promise_id
				status_message["details"]["politician_id"] = politician
				status_message["details"]["url"] = url

				try:
					promise_id = int(promise_id)
				except:
					promise_id = 0

				headers_list = request.headers.getlist("X-Forwarded-For")
				user_ip = headers_list[0] if headers_list else request.remote_addr
				if user_ip == '51.15.218.161':
					user_ip = "IP nem megállítható"

				dbc.cursor.execute("INSERT INTO submissions VALUES ('" + published_date + "','" + user_ip + "','" + url + "','" + source_name + "','" + article_title  + "','" + politician  + "','" + str(promise_id)  + "','" + str(datetime.datetime.now()) + "','" + submitter_name + "')")

				dbc.cursor.execute("SELECT id FROM submissions ORDER BY submitted_at DESC LIMIT 1")
				last_id = dbc.cursor.fetchone()[0]

				status_message["details"]["submission_id"] = last_id

				# return render_template("/submission_processor.html", status_message = status_message, static_content = "static content", page_properties = {"sidebar" : {"title" : "teszt", "contents" : "teszt"}})

			else:
				status_message["error"] = response.status_code + " HTTP hibakód a " + url
				email_content = request.remote_addr + ',' + str(datetime.datetime.now()) + ',' + politician + ',' + promise_id + ',' + url + str(response.status_code)
				send_email("Ígéretfigyelő: hibás cikkbeküldés: HTTP " + str(response.status_code), email_content)