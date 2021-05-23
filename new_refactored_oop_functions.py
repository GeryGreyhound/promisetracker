
from bs4 import BeautifulSoup
from PyPDF2 import PdfFileReader
import psycopg2
import psycopg2.extras
from psycopg2.extensions import AsIs

import datetime
import requests

import kemocloud_page_builder_v2
from common_functions import *



class DatabaseConnection:

	def __init__(self):
		config_file = "database.conf"

		with open(config_file) as config:
			db_config = config.read()
			
		self.connection = psycopg2.connect(db_config)
		self.connection.autocommit = True
		self.cursor = self.connection.cursor()
		self.dict_cursor = self.connection.cursor(cursor_factory=psycopg2.extras.DictCursor)



class Politician:
	def __init__(self, id, get_data = True):
		self.id = id
		self.existent = False
		
		try:
			self.get_basic_data()
		except:
			pass

		if self.existent and get_data == True:
			self.promise_list = PromiseListType2(self.id)
			self.generate_html()
			self.html += self.promise_list.promise_list_html


	def create_from_csv(self, csv_file, promise_title_col = 2, article_url_col = 3, suggested_status_col = 4, recsv = False, db_write = True):
		# article_url, suggested_status a CSV oszlopa, ha van sorszám akkor változik, szóval ne legyen hardcode-olva!
		dbc = DatabaseConnection()

		if recsv == True:
			db_write = False
		
		with open (csv_file, "r") as data:
			reader = csv.reader(data, delimiter = ";")

			print("Promisetracker CSV importer robot v0.1 alpha")
			politician_id = self.id
			category_counter = 0
			item_counter = 0
			for line in reader:
				re_line = None
			
				line[1] = line[1].replace("\t", "")
				
				
				# for x in range(175, 0, -1):
				#	if str(x) + ". " in line[1]:
				#		line[1] = line[1].replace(str(x) + ". ", "")
				
				if "info" in line[0]:
					print("Info:", line)
					sql_command = None
			
				elif line[0] == "cat" or line[0] == "CAT":
					category_counter += 1
					sql_command = "INSERT INTO promise_categories VALUES (%s, %s, %s);"
					sql_data = (politician_id, category_counter, decapitalize(line[1]))
					re_line = "{};{}".format("cat", decapitalize(line[1]) + "\n")
			
				elif line[0] == "item" or line[0] == "ITEM":
					item_counter += 1

					promise_title = line[promise_title_col]
					
					if recsv == True:
						promise_title = decapitalize(promise_title)
						pt_input = input(promise_title + "\n")
						if pt_input == "":
							pass
						else:
							promise_title = pt_input

					sql_command = "INSERT INTO promises VALUES (%s, %s, %s, %s, %s, %s);"
					sql_data = (item_counter, politician_id, category_counter, promise_title, "", [])
					if len(line) > 2:
						article_url = line[article_url_col]
						if article_url == "":
							suggested_status = ""
						else:
						
							article = Article(article_url)

							suggested_status = line[suggested_status_col].lower()
						
							article.get_meta_data()
							print(article.__dict__)
							article.add_to_submissions(self.id, item_counter, "CSV importer robot", "localhost", datetime.datetime.now(), suggested_status)
					else:
						article_url = suggested_status = ""


					re_line = "{};{};{};{};{}".format("item", item_counter, promise_title, article_url, suggested_status + "\n")
					
				try:
					print("SQL COMMAND:", sql_command, sql_data)
					if db_write == True:
						dbc.cursor.execute(sql_command, sql_data)
						print("DB WRITE: YES")
					else:
						print("DB WRITE: NO")
				except Exception as e:
					print("DB WRITE: FAILED:", e.args)
				
				if recsv == True and re_line:
					# miért ne csinálnánk inkább egy új csv-t, amivel már nincs szopás
					# aztán ha a névben benne van a recsv akkor azt máshogy kezeljük manuál inputok meg egyebek nélkül
					# ez egy 2 sör után jött ötlet, úgyhogy lekódolni tlaán már nem szerencsés így, de próbáljuk meg :)
	
					# 1: ha recsv van, akkor nincs DB írás, csak CSV fájl írás
					
	
					with open("recsv_" + self.id + ".csv", "a") as recsv_file:
						recsv_file.write(re_line)

		dbc.connection.close()

	def get_basic_data(self):
		dbc = DatabaseConnection()
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

			self.passed_months = diff_month(self.start_date,datetime.datetime.now())
			self.remaining_months = -1*(diff_month(datetime.datetime.now(),self.end_date))-1
			self.passed_days = (datetime.datetime.now() - self.start_date).days
			self.total_days = (self.end_date - self.start_date).days

			self.days_percentage = round((self.passed_days / self.total_days) * 100, 2)
			self.date_progress = {"start_date" : self.start_date, 
								  "end_date" : self.end_date,
								  "passed_months" : self.passed_months, 
								  "remaining_months" : self.remaining_months,
								  "days_percentage" : self.days_percentage}

		else:
			self.existent = False

	def generate_html(self):
		self.html = kemocloud_page_builder_v2.PromisetrackerAddOn.custom_html["date_progress"].format(**self.date_progress)



class PromiseListType2:

	def __init__(self, politician_id):
		self.politician_id = politician_id
		self.promises = list()
		self.promise_categories = list()
		self.status_counters = {"promises" : 0, "none": 0, "success" : 0, "pending" : 0, "partly" : 0, "problem" : 0, "fail" : 0}
		self.status_percentages = dict()
		self.loop_counter_test = 0

		dbc = DatabaseConnection()

		categories_query = "SELECT * FROM promise_categories WHERE politician_id = (%s) ORDER BY category_id"
		query_data = [self.politician_id]
		dbc.cursor.execute(categories_query, query_data)
		promise_categories = dbc.cursor.fetchall()

		promises_query = "SELECT * FROM promises WHERE politician_id = (%s) ORDER BY id" # AND category_id = (%s) AND (custom_options != 'draft' OR custom_options IS NULL) ORDER BY id"
		query_data = [self.politician_id]
		dbc.cursor.execute(promises_query, query_data)
		promises = dbc.cursor.fetchall()

		articles_query = "SELECT * FROM news_articles WHERE politician_id = (%s) ORDER BY article_date DESC"
		query_data = [self.politician_id]
		dbc.cursor.execute(articles_query, query_data)
		articles = dbc.cursor.fetchall()

		subitems_query = "SELECT * FROM subitems WHERE politician_id = (%s) ORDER BY sub_id"
		query_data = [self.politician_id]
		dbc.cursor.execute(subitems_query, query_data)
		sub_items = dbc.cursor.fetchall()

		dbc.connection.close()

		for category in promise_categories:
			current_category = dict()
			current_category["category_id"] = category[1]
			current_category["name"] = category[2]
			current_category["promise_list"] = list()
			self.promise_categories.append(current_category)

		for promise in promises:
			current_promise = Promise(politician_id = self.politician_id, promise_id = promise[0])
			current_promise.category_id = promise[2]
			current_promise.name = promise[3]
			current_promise.custom_options = promise[4]
			if not current_promise.custom_options:
				current_promise.custom_options = list()
			current_promise.sub_items = list()
			for sub_item in sub_items:
				parent_id = sub_item[1]
				if parent_id == current_promise.id:
					current_promise.sub_items.append(sub_item)
			current_promise.articles = list()
			current_promise.status = "none"

			self.promises.append(current_promise)

		for article in articles:
		
			current_article = Article()
			current_article.date = article[0]
			current_article.url = article[1]
			current_article.source_name = article[2]
			current_article.title = article[3]
			current_article.promise_id = article[5]
			current_article.promise_status = article[6]

			promise_position_in_list = current_article.promise_id - 1

			if current_article.promise_id != 0:
				self.promises[promise_position_in_list].articles.append(current_article)

		for promise in self.promises:

			if not "draft" in promise.custom_options:
				category_position_in_list = promise.category_id - 1

				if len(promise.articles) > 0:
					promise.status = promise.articles[0].promise_status

				self.status_counters[promise.status] += 1
				self.status_counters["promises"] += 1
				self.promise_categories[category_position_in_list]["promise_list"].append(promise)

		needed_statuses = ["success", "partly", "pending"]

		for ns in needed_statuses:
			self.status_percentages[ns] = round((self.status_counters[ns] / self.status_counters["promises"]) * 100, 2)

		self.generate_html()

	def generate_html(self):
		

		self.promise_list_html = ""

		status_counters_html = kemocloud_page_builder_v2.PromisetrackerAddOn.custom_html["status_counters"].format(**self.status_percentages)
		self.promise_list_html += status_counters_html

		for promise_category in self.promise_categories:
			category_promises_html = ""

			for promise in promise_category["promise_list"]:

				promise.html = ""
				articles_list_html = ""

				if len(promise.articles) > 0:

					promise.news_info_icon = kemocloud_page_builder_v2.PromisetrackerAddOn.custom_html["promise_list_news_info_icon"].format(article_count = len(promise.articles))

					for article in promise.articles:
						current_article_html = kemocloud_page_builder_v2.PromisetrackerAddOn.custom_html["promise_list_item_news_list_item"].format(**article.__dict__)
						articles_list_html += current_article_html + "\n"

				else:
					promise.news_info_icon = kemocloud_page_builder_v2.PromisetrackerAddOn.custom_html["promise_list_no_news_icon"]

				sub_items_list_html = ""
				if len(promise.sub_items) > 0:

					sub_items_list_html = ""
					
					for sub_item in promise.sub_items:
						sub_items_list_html += "<li>" + str(sub_item[3]) + "</li>\n"

					sub_items_list_html = '<div class="subitems_wrapper" style="display: table-row;"><div style="display: table-cell;"></div><div style="display: table-cell;"></div><ul style="display: table-cell; width: 100%;">' + sub_items_list_html + "</ul></div>"

				promise.sub_items = sub_items_list_html


				# még hozzágeneráljuk az ojjekt variable-ökhöz a státusz színes CSS baszt, meg a többi státusz izét a kemocloud_page_builder_v2.PromisetrackerAddOn.custom_html["promise_list_item"]
				# struktúrájának megfelelően, hogy már tényleg azt is csak annyi legyen letudni, hogy .format(**promise.__dict__) oszt jónapot. SIMPLICITY ÜBER ALLES!!!!

				promise_status_css_classes = {
					"none" : "badge badge-secondary",
					"pending" : "badge badge-primary",
					"partly" : "badge badge-info",
					"success" : "badge badge-success",
					"problem" : "badge badge-warning",
					"failed" : "badge badge-danger"
				} # ennek is a GLOBAL_SETTINGS-ben kéne majd lennie testreszabhatóan!!!!

				promise.status_css_class = promise_status_css_classes[promise.status]
				promise.status_title = "folyamatban" # ezt valahogy a stringsből kell, de van-e itt stringsünk? Kéne h legyen, sőt, a Routesben nem kéne, ez is backend feladat tehát itt kell lennie ebben a .PY-ben
				promise.articles_list = articles_list_html
				promise.html = kemocloud_page_builder_v2.PromisetrackerAddOn.custom_html["promise_list_item"].format(**promise.__dict__)
				category_promises_html += promise.html


			category_html = kemocloud_page_builder_v2.PromisetrackerAddOn.custom_html["promise_list_category"].format(name = promise_category["name"], category_items = category_promises_html)
			self.promise_list_html += category_html	



class Promise:
	def __init__(self, politician_id, promise_id):
		self.politician_id = politician_id
		self.id = promise_id
		self.status = "none"




class Article:
	def __init__(self, url = None):
		
		self.url = url
		self.errors = list()

	def get_from_database(self, policitian_id, promise_id):
		pass

	def get_meta_data(self): # from web when submitted

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
					try:
						title, junk = title_string.split(" - ")
						self.source_name = "Facebook - " + title
					except:
						title = "Cím beolvasása nem sikerült"
						self.source_name = "Facebook"
					
					self.article_title = None
					self.errors.append("get_title_error")


				# D) check if the article has an OG-image:
				try:
					self.image_url = soup.find("meta",  attrs={'property': 'og:image'})['content']
				except:
					self.image_url = None

	def get_from_database(self):
		pass

	def add_to_submissions(self, politician_id, promise_id, submitter_name, submitter_ip, submit_date, suggested_status):
		# ezt lehet, hogy inkább egy Submission class-ben kéne intézni? És annak lesz egy self.article-je, akkor nem kell ez a sok szarság
		dbc = DatabaseConnection()
		
		checkable_variables = [self.title, self.source_name, self.date]

		self.title = sql_injection_filter(self.title)
		self.source_name = sql_injection_filter(self.source_name)

		dbc.cursor.execute("SELECT id FROM submissions ORDER BY id DESC LIMIT 1")
		last_id = dbc.cursor.fetchone()[0]
		new_id = last_id + 1
		
		query_string = "INSERT INTO submissions VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)"
		query_data = [self.date, submitter_ip, self.url, self.source_name, self.title, politician_id, promise_id, submit_date, submitter_name, new_id, None, None, suggested_status]

		dbc.cursor.execute(query_string, query_data)

		dbc.connection.close()


class ArticleList:
	pass
	# eldöntendő: ez legyen így, vagy a Politician object tartalmazza?
	# elvégre ott minden, az adott politikushoz tartozó hírt queryzünk és az object tartalmazza,
	# semeddig nem tart egy sima list-be is tenni, ahogy a /news oldalra kell.
	#simplicity #RUSHIT2104


class Submission:
	def __init__(self):
		pass

	def create_from_url(self, url, politician_id, promise_id):
		self.url = url
		self.politician_id = politician_id
		self.promise_id = promise_id

		self.article = Article(url = self.url)
		self.article.get_meta_data()
		# ide a lenti mainből még megmaradt régi functionjei, amik berakják a submission table-be és létrehozzák a sikeres beküldés oldalt





class User:
	def __init__(self, login_id):
		pass

	# user létrehozása: belépéskor vagy? Elvileg csak belépéskor TEHÁT lehet kezdeni login ID-vel (ami email)












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