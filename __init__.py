from flask import Flask, Markup, render_template, session, request, redirect
from bs4 import BeautifulSoup
from email.mime.text import MIMEText as text
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import datetime
import sys
import os
import psycopg2
from psycopg2.extensions import AsIs
from passlib.hash import sha256_crypt
import requests
import smtplib
import socket
import time

os.chdir("/var/www/igeretfigyelo/igeretfigyelo")
sys.path.insert(0, os.getcwd())

from common_functions import send_email
import new_refactored_oop_functions as promisetracker_v2

promise_statuses = {"none" : "meghirdetve", "pending" : "folyamatban", "partly" : "részben", "success" : "sikeres", "problem" : "problémás", "failed" : "meghiúsult"}

MAIN_SETTINGS = dict()
MAIN_SETTINGS["DEBUG_OPTIONS"] = False

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True

class DatabaseOperations:

	def __init__(self):
		config_file = "database.conf"

		with open(config_file) as config:
			db_config = config.read()
			
		self.connection = psycopg2.connect(db_config)
		self.connection.autocommit = True
		self.cursor = self.connection.cursor()


def get_politician_data(politician):
	dbc = DatabaseOperations()
	dbc.cursor.execute("SELECT * FROM politicians WHERE id = '" + politician + "';")
	selected_politician = dbc.cursor.fetchone()
	try:
		if len(selected_politician) == 0:
			return False
	except:
		return False

	return selected_politician


def sql_injection_filter(string):

	message = ""
	if string.find("DROP") != -1:
		message = Markup('SQL injection :) LOL nemá, ez annyira 2008... <br><br>Örülj neki, hogy nem 2008 van, mert most átirányítanálak a <a href="http://nobrain.dk">nobrain.dk</a>-ra :) Sajnos már kinyírták a modern webes technológiák, úgyhogy sajnos csak annyit tehetek, hogy logolom az IP-d, és figyellek, ha még egyszer ilyesmivel próbálkozol (fiatalok kedvéért: régen ez az oldal automatikusan ide-oda ugrált a monitoron bezárhatatlanul, a legjobb prank volt a neten, ha meg akartál szívatni valakit :)))')
	elif string.find("1=1") != -1 or string.find("1 = 1") != -1:
		message = "1 egyenlő 1-gyel, ha ezt eddig nem tudtad, akkor most már tudod. De miért tőlem kérdezed? Azt hitted, megszánlak, hogy milyen buta vagy, és cserébe szabadon engedlek garázdálkodni a szerveren? Hát... Nem nyert."
	elif ";" in string:
		message = "Érvénytelen karakter a címben. Nem tudom, mivel próbálkozol, de inkább ne tedd."
	else:
		return string
	return message

def diff_month(d1, d2):
	return (d1.year - d2.year) * 12 + d1.month - d2.month

source_replaceable_url_parts = {"m.hvg.hu" : "hvg.hu"}

sources = {"facebook.com/133909266986" : "Facebook - VEKE",
		  "facebook.com/vekehu" : "Facebook - VEKE",
		  "facebook.com/karacsonygergely" : "Facebook - Karácsony Gergely",
		  "facebook.com/budapestmindenkie" : "Facebook - Budapest Városháza",
		  "index.hu" : "Index",
		  "telex.hu" : "Telex",
		  "444.hu" : "444",
		  "vastagbor.atlatszo" : "Vastagbőr blog"
		  }

def fetch_article_data(article_url, soup):
	metas = soup.find_all('meta')
	try:
		article_title = sql_injection_filter(soup.find("meta",  attrs={'name':'title'})['content'])
	except:
		try:
			article_title = sql_injection_filter(soup.find("meta",  attrs={'property': 'og:title'})['content'])
		except:
			try:
				article_title = sql_injection_filter(soup.find("title").string)
			except:
				article_title = " [cím beolvasása nem sikerült]"
	try:
		published_date = sql_injection_filter(soup.find("meta",  attrs={'property': 'article:published_time'})['content'])
	except:
	
		try:
			url_parts = list(article_url.split("/"))
			for counter, part in enumerate(url_parts):
				if counter < len(url_parts) - 3:
					try:
						year, month, day = int(url_parts[counter]), int(url_parts[counter+1]), int(url_parts[counter+2])
						print("year, month, day",year, month, day)
						
						published_date = datetime.datetime(year, month, day).strftime("%Y-%m-%d")

					except:
						pass
						
		
		except:
			published_date = '1982-01-18'


	x, source_url = article_url.split("//")
	source_url, y = source_url.split("/", 1)

	for srp in source_replaceable_url_parts:
		source_url = source_url.replace(srp, source_replaceable_url_parts[srp])

	source_name = source_url

	for src in sources:
		if src in source_url:
			source_name = sources[src]

	if "Telex: " in article_title:
		article_title = article_title.replace("Telex: ", "")

	if "facebook" in article_url:
		title_string = sql_injection_filter(soup.find("title").string)
		print(title_string)
		title, junk = title_string.split(" - ")
		source_name = "Facebook - " + title
		article_title = " [cím beolvasása nem sikerült]"

	try:
		return article_title, published_date, source_name
	except:
		return article_title, "1982-01-18", source_name





@app.before_request
def before_request_func():
	
	if not "version" in session or "v" in request.args:
		session["version"] = request.args.get("v")
		if not session["version"]:
			session["version"] = "1"

	headers_list = request.headers.getlist("X-Forwarded-For")
	user_ip = headers_list[0] if headers_list else request.remote_addr

	skip_list = [".js", ".ico"]
	print_req = True
	for item in skip_list:
		if item in request.url:
			print_req = False

	try:
		if MAIN_SETTINGS["DEBUG_OPTIONS"] == False:
			kc1122_ip = socket.gethostbyname("kemocloud-1122.dyndns.hu")
		else:
			kc1122_ip = ""

		if user_ip == kc1122_ip:
			print_req = False
	except:
		pass

	if print_req:
		print(user_ip, request.url)
		with open ("/var/www/igeretfigyelo/igeretfigyelo/access_log.csv", "a") as logfile:
			logfile.write(datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "," + str(user_ip) + "," + str(request.url) + "," + str(request.referrer) + "\n")

	if request.referrer:
		if "best-proxies.ru" in request.referrer:
			print("Orosz izé redirectelve")
			return redirect("https://www.pornhub.com/gayporn")
			
@app.route("/", methods = ["POST", "GET"])
def main_page():
	return redirect("/about")

@app.route("/about")
def about_page():
	page_properties = dict()
	page_properties["og-title"] = "ÍgéretFigyelő"
	page_properties["sidebar"] = {"title" : "Egyedi sidebar", "content" : "teszt"}

	return render_template("igeretfigyelo_about.html", page_properties = page_properties, static_content = "static_content")

@app.route("/contact", methods = ["POST", "GET"])
def contact_page():
	page_properties = dict()
	page_properties["og-title"] = "ÍgéretFigyelő"
	page_properties["sidebar"] = {"title" : "Egyedi sidebar", "content" : "teszt"}

	if request.method == "POST":
		from_address = request.form.get("email")
		from_name = request.form.get("name")
		subject = request.form.get("subject")
		text = request.form.get("message")
		verify = request.form.get("verify")

		if str(verify) != "7":
			vf = "[Ígéretfigyelő spam gyanús]"
		else:
			vf = "[Ígéretfigyelő contact]"

		send_email(vf + subject, {"html" : text, "text" : text}, {"email_list" : ["igeretfigyelo.kemo@gmail.com"]})

		return render_template("contact.html", page_properties = page_properties, static_content = "static_content", success = True)

	else:	
		return render_template("contact.html", page_properties = page_properties, static_content = "static_content")

@app.route("/accept_invite")
def invite():
	dbc = DatabaseOperations()
	page_properties = dict()
	email = request.args.get("email")
	
	dbc.cursor.execute("SELECT * FROM invitations WHERE email = (%s)", [email])
	
	invitation_data = dbc.cursor.fetchone()
	page_properties["errors"] = None

	if invitation_data:

		page_properties["email"] = email
		page_properties["display_name"] = invitation_data[1]
		page_properties["selected_politician"] = invitation_data[2]

	else:

		page_properties["errors"] = ["ehhez az e-mailcímhez nem tartozik meghívó"]
		page_properties["disabled"] = True

	page_properties["politicians"] = {"karacsonygergely" : "Karácsony Gergely", "shrekszilard" : "Shrek Szilárd (az oldal funkcióinak tesztelését segítő teszt politikus)", "csoziklaszlo" : "Csőzik László", "fulopzsolt": "Fülöp Zsolt"}
	
	page_properties["sidebar"] = {"title" : "Egyedi sidebar", "content" : "teszt"}

	return render_template("invite.html", page_properties = page_properties, static_content = "static_content")

@app.route("/reset_gj")
def gipsz_jakab():
	dbc = DatabaseOperations()
	dbc.cursor.execute("INSERT INTO invitations VALUES (%s, %s, %s)", ["gipsz.jakab@gmail.com", "Gipsz Jakab", "csoziklaszlo"])
	dbc.cursor.execute("SELECT * FROM users WHERE email = 'gipsz.jakab@gmail.com'")

	gj_data = dbc.cursor.fetchone()
	gj_id = gj_data[0]

	dbc.cursor.execute("DELETE FROM users WHERE email = 'gipsz.jakab@gmail.com'")
	dbc.cursor.execute("DELETE FROM user_permissions WHERE user_id = (%s)", [gj_id])

	return("ok")
	

@app.route("/register", methods = ["POST"])
def register():
	dbc = DatabaseOperations()
	display_name = request.form.get("display_name")
	password_1 = request.form.get("password1")
	password_2 = request.form.get("password2")
	email = request.form.get("invite_email")
	page_properties = dict()
	page_properties["errors"] = list()
	page_properties["success"] = None

	dbc.cursor.execute("SELECT * FROM invitations WHERE email = (%s)", [email])
	invitation_data = dbc.cursor.fetchone()
	selected_politician = invitation_data[2]

	if not display_name or display_name == "":
		page_properties["errors"].append("Név megadása kötelező")
	if not password_1 or not password_2 or password_1 == "" or password_2 == "":
		page_properties["errors"].append("Jelszó megadása kötelező")
	if password_1 != password_2:
		page_properties["errors"].append("A megadott jelszavak nem egyeznek")
	if not email or email == "":
		page_properties["errors"].append("E-mailcím megadása kötelező")

	if len(page_properties["errors"]) == 0:
		page_properties["errors"] = None
		page_properties["success"] = True

		selected_politician = invitation_data[2]

		dbc.cursor.execute("SELECT * FROM users ORDER BY id DESC LIMIT 1")
		last_user = dbc.cursor.fetchone()
		last_user_id = last_user[0]
		new_user_id = last_user_id + 1

		dbc.cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s)", [new_user_id, email, password_1, "limited", display_name])
		dbc.cursor.execute("INSERT INTO user_permissions VALUES (%s, %s)", [new_user_id, selected_politician])
		dbc.cursor.execute("INSERT INTO user_permissions VALUES (%s, %s)", [new_user_id, "shrekszilard"])
		dbc.cursor.execute("DELETE FROM invitations WHERE email = (%s)", [email])

	page_properties["sidebar"] = {"title" : "Egyedi sidebar", "content" : "teszt"}

	
	return render_template("invite.html", page_properties = page_properties, static_content = "static_content")

@app.route("/news")
def news_page():
	dbc = DatabaseOperations()
	politician = request.args.get("politician_name")
	selected_politician = get_politician_data (politician)

	if not selected_politician:
		return ("error.html helye, error: politician_not_in_database") # majd return error.html, error = not in database


	try:
		dbc.cursor.execute ("SELECT * FROM news_articles WHERE politician_id = (%s) ORDER BY article_date DESC", (politician,))
	except:
		return ("error.html helye, error: politician_not_in_database")
	latest_news = dbc.cursor.fetchall()
	latest_news_formatted = list()

	for article in latest_news:
		article_details = dict()
		article_details["date"] = str(article[0])[:10]
		article_details["url"] = article[1]
		article_details["source"] = article[2]
		article_details["title"] = article[3]
		latest_news_formatted.append(article_details)

	status_message = ""

	page_properties = {"name" : selected_politician[1], 
					   "location" : selected_politician[2], 
					   "title" : selected_politician[3], 
					   "sidebar" : {"title" : selected_politician[1] + " névjegye", "content": {"newsfeed" : latest_news_formatted}},
					   "status_message" : status_message}

	return render_template("news.html", news = latest_news_formatted, static_content = "static content", page_properties = page_properties)



def get_users_politicians(user_id):
	dbc = DatabaseOperations()
	dbc.cursor.execute("SELECT * FROM users WHERE id = (%s)", [user_id])
	selected_user = dbc.cursor.fetchone()

	if selected_user[3] == "full":
		dbc.cursor.execute("SELECT id FROM politicians") 
		# to-do: itt legyen majd lokáció meg titulus is, mert az adminmenüben áttekinthetetlen lesz idővel hogy ki kicsoda
		# to-do: politicians táblában legyen public kapcsoló, hogy az Ígéretfigyelő kezdőlapján (/about) megjelenjen_e

	else:
		dbc.cursor.execute("SELECT politician_id FROM user_permissions WHERE user_id = (%s)", [str(selected_user[0])])

	politicians = dbc.cursor.fetchall()
	allowed_politicians = list()

	for p in politicians:
		politician_id = p[0]
		dbc.cursor.execute("SELECT name FROM politicians WHERE id = (%s)", [politician_id])
		p_name = dbc.cursor.fetchone()

		allowed_politicians.append({"id" : politician_id, "name" : p_name[0]})

	return allowed_politicians

@app.route("/logout")
def session_reset():
	session.clear()
	return redirect("/login")

@app.route("/ifadmin")
def admin_page():
	if "debug_mode" in request.args:
		MAIN_SETTINGS["DEBUG_OPTIONS"] = True
	else:
		MAIN_SETTINGS["DEBUG_OPTIONS"] = False
	if "validate_required" in request.args:
		validate_required = True

	edit_feedback = dict()

	feedback_items = {"s" : "saved", "d" : "deleted", "n" : "error"}

	for key, value in feedback_items.items():

		edit_feedback[value] = list()
		if key in request.args:
			edit_feedback[value] = list(request.args.get(key).split("_"))



	page_properties = dict()
	sidebar = dict()
	sidebar_content = {"title" : "Admin menü", "contents" : ""}

	page_properties["sidebar"] = sidebar_content
	page_properties["og-title"] = "IFadmin"
	page_properties["edit_feedback"] = edit_feedback
	error = ""
	dbc = DatabaseOperations()

	if "logged_in" in session:

		dbc.cursor.execute("SELECT * FROM users WHERE id = (%s)", [session["user_id"]])
		user_data = dbc.cursor.fetchone()

		politicians = get_users_politicians(session["user_id"])

		page_properties["politicians_promises"] = dict()
		page_properties["promise_statuses"] = promise_statuses

		for politician in politicians:
			current_politicians_promises = list()
			dbc.cursor.execute("SELECT id, name FROM promises WHERE politician_id = (%s) ORDER BY id", [politician["id"]])
			promises = dbc.cursor.fetchall()
			for promise in promises:
				current_politicians_promises.append({"id" : promise[0], "title" : promise[1]})

			page_properties["politicians_promises"][politician["id"]] = current_politicians_promises


		#kell a felhasználó összes politikusának összes ígérete az ígéret dropdownhoz
		#ezek legyenek egy dictben



		pols_query_list = '('

		for counter, pol in enumerate(politicians):
			pols_query_list += "'" + pol["id"] + "'"
			if counter+1 < len(politicians):
				pols_query_list += ","

		pols_query_list += ")"

		sub_query = '''
			select * from submissions 
			join politicians on politicians.id = submissions.politician_id 
			left join promises on promises.id = submissions.promise_id and promises.politician_id = submissions.politician_id
			left join users on submissions.confirmed_by = users.id
			where submissions.politician_id in ---list---
			order by submitted_at desc
			'''.replace("---list---", pols_query_list)

		dbc.cursor.execute(sub_query)
		submissions_list = dbc.cursor.fetchall()



		submissions = list()
		submissions_test = ""
	
		for sub in submissions_list:
			current = dict()
			current["date"] = sub[0].strftime("%Y-%m-%d")
			if current["date"] == "1982-01-18":
				current["date"] = ""
			
			current["url"] = sub[2]
			current["source_name"] = sub[3]
			current["title"] = sub[4]
			current["politician_id"] = sub[5]
			current["promise_id"] = sub[6]
			current["submission_date"] = (sub[7]+datetime.timedelta(hours = 2)).strftime("%Y-%m-%d %H:%M:%S")
			current["submitted_by"] = sub[8]
			current["submission_id"] = str(sub[9]).zfill(5)
			
			confirm_status = sub[10]
			try:
				current["confirm_level"], current["confirm_value"] = confirm_status.split("_")
			except:
				current["confirm_level"] = current["confirm_value"] = "none"

			current["confirmed_by"] = sub[11]
			current["suggested_status"] = sub[12]
	
			if sub[13]:
				current["validation_errors"] = sub[13]

			current["politician_name"] = sub[15]
			
			current["custom_options"] = str(sub[25])
			current["confirmer_user_permissions"] = sub[30]
			current["confirmed_by_display_name"] = sub[31]

			if not current["submitted_by"]:
				current["submitted_by"] = "vendég (IP cím: " + sub[1] + ")"
			
			dbc.cursor.execute("SELECT promise_status FROM news_articles WHERE politician_id = (%s) AND promise_id = (%s) LIMIT 1", [current["politician_id"], current["promise_id"]])
			ps = dbc.cursor.fetchone()
			if ps:
				current["promise_status_id"] = ps[0]
			else:
				current["promise_status_id"] = "none"
				
			current["promise_status_title"] = promise_statuses[current["promise_status_id"]]


			# mivel a query eleve csak azokhoz a politikusokhoz tartozó ígéreteket queryzi, amikhez a session usernek joga van, itt már nem kell ezt szűrni

			# VISZONT el kell dönteni, hogy miket mutasson: a limited szerkesztő által véglegesítetteket már ne, csak adminnak, az admin által véglegesítetteket meg senkinek, csak ha be van kapcsolva ez
			# to-do: kapcsoló a tetejére az adminoknak (mutassa a véglegesítetteket is, és ezek legyenek szerkeszthetők utólag is)

			# MUTATNI KELL, ha:

			must_show = False

			# admin a session user...
			if session["user_type"] == "full":
				#... és admin nem véglegesítette még (vagy senki), akkor mutatni kell:
				if current["confirmer_user_permissions"] != "full":
					must_show = True
				#... ha admin véglegesítette, akkor nem kell:
				if current["confirmer_user_permissions"] == "full" and current["confirm_level"] == "confirmed":
					must_show = False
				#... és admin csak jelölte, akkor is kell
				if current["confirmer_user_permissions"] == "full" and current["confirm_level"] == "marked":
					must_show = True

			# limited a session user, és ő mentette
			if session["user_type"] == "limited":
				if current["confirmed_by"] == session["user_id"]:
					must_show = True
				if current["confirmed_by"] != session["user_id"]:
					must_show = False
				if current["confirm_level"] == "confirmed":
					must_show = False

			# ha nincs státusz, mindenképp kell
			if current["confirm_value"] == "none":
				must_show = True


			# NEM KELL MUTATNI, ha:

			# limited a session user, és valaki más limited user már mentette (az már legyen az övé)


			# ha confirmed a confirm_level, és az confirmed_by megegyezik a session userrel, akkor nem kell mutatni
			# ha confirmed, és nem egyezik meg, ÉS admin a session_user, akkor mutatni kell
			# ha confirmed, és megegyezik, és admin az user, akkor se

			# akkor kell még mutatni, ha nem confirmed
			if must_show == True:
				submissions.append(current)
				submissions_test += str(current) + "<br>"
			else:
				pass
				# print ("DEBUG: must_show = False ennél a rekordnál: ", str(current))

		# return Markup(submissions_test)


		pol_list = "<p>"
		for politician in politicians:
			pol_list += "<a href=/" + politician["id"] + ">" +  politician["name"] + "</a><br>"

		if user_data[3] == "full":
			pol_list += '</p><p>&nbsp&nbsp<a href="/add_politician"><b>új hozzáadása</b></a>'
			user_permission = "Teljeskörű"

		else:
			user_permission = "Szerkesztő"

		pol_list += "</p>"


		admin_menu_html = '''
		<p><b>Felhasználó</b></p>
		<p>bejelentkezve, mint {}<br>Jogosultsági szint: {}</p>
		<p><a href=/profile>adataim</a><br>
		<a href=/logout>kijelentkezés</a></p>
		<hr>
		<p><b>Politikusok</b></p>
		{}
		<hr>
		<p>Beküldött cikkek <b>({})</b></p>
		<hr>
		<p><a href=/activity_log>tevékenységnapló</a></p>
		'''.format(session["user_name"], user_permission, pol_list, str(len(submissions)))

		page_properties["sidebar"]["contents"] = Markup(admin_menu_html)

		return render_template("admin.html", static_content = "static content", submissions_list = submissions, page_properties = page_properties, error = error, admin_mode = True, debug_mode = MAIN_SETTINGS["DEBUG_OPTIONS"])

	else:
		return redirect("/login")



@app.route("/login", methods=["POST", "GET"])
def ifadmin_login():

	page_properties = dict()
	sidebar = dict()
	sidebar_content = dict()

	sidebar["content"] = sidebar_content
	# sidebar["title"] = "Adminisztrációs menü"
	page_properties["sidebar"] = sidebar
	page_properties["og-title"] = "IFadmin"
	error = ""
	dbc = DatabaseOperations()

	if "logged_in" not in session:

		if request.method == "POST":
		
			user_email = sql_injection_filter(request.form["email"])
			user_password = sql_injection_filter(request.form["password"])

			dbc.cursor.execute("SELECT * FROM users WHERE email = (%s)", [user_email])
			
			selected_user = dbc.cursor.fetchone()

			if not selected_user:
				return "error.html helye, hiba: user_not_found"

			elif user_password != selected_user[2]:
				return "error.html helye, hiba: incorrect_password"

			else:
				session["logged_in"] = True
				session["user_id"] = selected_user[0]
				session["user_name"] = selected_user[4]
				session["user_type"] = selected_user[3]

			return redirect("/ifadmin")

		else:
			return render_template("admin.html", static_content = "static content", page_properties = page_properties, error = error, admin_mode = True, debug_mode = MAIN_SETTINGS["DEBUG_OPTIONS"])

class r_error:
	def __init__(self):
		pass

@app.route("/<politician>", methods = ["POST", "GET"])
def igeretfigyelo_page(politician):

	benchmark_start_time = datetime.datetime.now()
	print("V1 benchmark: request received", datetime.datetime.now())

	if session["version"] == "2":
		pass
	else:
		pass

	# politician = request.args.get("politician_name")
	selected_promise_id = request.args.get("promise_id")
	dbc = DatabaseOperations()

	# print ("y", politician, request.method)
	status_message = dict()

	if "submission_success" in request.args:
		submission_id = request.args.get("submission_success")

		dbc.cursor.execute("SELECT * FROM submissions WHERE id = (%s)", [str(submission_id)])
		submission = dbc.cursor.fetchone()
		status_message["details"] = dict()

		submission_status_items = ["Cikk dátuma", "Beküldő IP címe", "Link", "Forrás", "Cím", "Politikus azonosítója", "Ígéret sorszáma", "Beküldés dátuma"]

		for counter, item in enumerate(submission_status_items):
			value = str(submission[counter])
			if len(str(value)) > 50:
				value = value[:50] + "..."
			if value == 0:
				value = "0 (új)"
			status_message["details"][item] = value

		status_message["success"] = "Sikeres cikkbeküldés, köszönjük!"

	if request.method == "POST":
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

					dbc.cursor.execute("SELECT id FROM submissions ORDER BY id desc LIMIT 1")
					last_id = dbc.cursor.fetchone()[0]

					dbc.cursor.execute("INSERT INTO submissions VALUES ('" + published_date + "','" + user_ip + "','" + url + "','" + source_name + "','" + article_title  + "','" + politician  + "','" + str(promise_id)  + "','" + str(datetime.datetime.now()) + "','" + submitter_name + "','" + str(last_id+1) + "')")

					dbc.cursor.execute("SELECT id FROM submissions ORDER BY submitted_at DESC LIMIT 1")
					last_id = dbc.cursor.fetchone()[0]

					status_message["details"]["submission_id"] = last_id

					return render_template("/submission_processor.html", status_message = status_message, static_content = "static content", page_properties = {"sidebar" : {"title" : "teszt", "contents" : "teszt"}})

				else:
					status_message["error"] = response.status_code + " HTTP hibakód a " + url
					email_content = request.remote_addr + ',' + str(datetime.datetime.now()) + ',' + politician + ',' + promise_id + ',' + url + str(response.status_code)
					send_email("Ígéretfigyelő: hibás cikkbeküldés: HTTP " + str(response.status_code), email_content)

	if not politician:
		return Markup("about.html helye<br><a href='?politician_name=karacsonygergely'>Karácsony Gergely</a>")

	politician_filtered = sql_injection_filter(politician)
	if politician_filtered != politician:
		return "error.html helye, hiba: érvénytelen kérés"

	dbc.cursor.execute("SELECT * FROM politicians WHERE id = '" + politician + "';")
	selected_politician = dbc.cursor.fetchone()

	try:
		if len(selected_politician) == 0:
			return "error.html helye, hiba: nincs az adatbázisban ilyen"
	except:
		return "error.html helye, hiba: nincs az adatbázisban ilyen"

	
	else:
		print("V1 benchmark: getting news articles", datetime.datetime.now())
		dbc.cursor.execute ("SELECT * FROM news_articles WHERE politician_id = '" + politician + "' ORDER BY article_date DESC LIMIT 10")
		latest_news = dbc.cursor.fetchall()
		latest_news_formatted = list()

		for article in latest_news:
			article_details = dict()
			article_details["date"] = str(article[0])[:10]
			article_details["url"] = article[1]
			article_details["source"] = article[2]
			article_details["title"] = article[3]
			latest_news_formatted.append(article_details)




		
		# dbc.cursor.execute("SELECT * FROM promise_categories JOIN promises ON promises.category_id = promise_categories.category_id WHERE promises.politician_id = '" + politician + "' ORDER BY promises.id;")
		



		# refactor class PromiseList innen!!!

		dbc.cursor.execute ("SELECT * FROM promise_categories WHERE politician_id = '" + politician + "' ORDER BY category_id")
		promise_categories = dbc.cursor.fetchall()

		promise_counter = 0
		success_counter = 0
		pending_counter = 0
		fail_counter = 0
		partly_counter = 0

		promises_list = list()
		
		for category in promise_categories:
			category_details = dict()
			category_details["title"] = category[2]

			category_id = category[1]
			dbc.cursor.execute ("SELECT * FROM promises WHERE politician_id = %s AND category_id = %s AND (custom_options != 'draft' OR custom_options IS NULL) ORDER BY id", [politician, AsIs(str(category_id))])
			category_promises = dbc.cursor.fetchall()

			category_promises_list = list()

			for promise in category_promises:
				promise_details = dict()

				promise_id = promise[0]
				promise_counter += 1
				dbc.cursor.execute ("SELECT * FROM news_articles WHERE politician_id = '" + politician + "'AND promise_id = " + str(promise_id) + "ORDER BY article_date DESC")
				promise_articles = dbc.cursor.fetchall()

				dbc.cursor.execute ("SELECT * FROM subitems WHERE politician_id = '" + politician + "'AND parent_id = " + str(promise_id) + "ORDER BY sub_id")
				promise_subitems = dbc.cursor.fetchall()

				promise_articles_list = list()
				
				if len(promise_articles) > 0:

					promise_details["status"] = promise_articles[0][6]
					for article in promise_articles:
						article_details = dict()
						article_details["date"] = article[0]
						article_details["url"] = article[1]
						article_details["source"] = article[2]
						article_details["title"] = article[3]
						article_details["status"] = article[6]
	
						promise_articles_list.append(article_details)

				else:
					promise_details["status"] = "none"
	
				
				promise_details["articles"] = promise_articles_list
				promise_details["id"] = promise_id

				subitems_list = list()

				if len (promise_subitems) > 0:

					for subitem in promise_subitems:
						subitem_details = dict()
						subitem_details["parent_id"] = subitem[1]
						subitem_details["id"] = subitem[2]
						subitem_details["title"] = subitem[3]
						subitems_list.append(subitem_details)
	
				promise_details["subitems"] = subitems_list

				

				if promise_details["status"] == "success":
					success_counter += 1
				if promise_details["status"] == "failed":
					fail_counter += 1
				if promise_details["status"] == "pending":
					pending_counter += 1
				if promise_details["status"] == "partly":
					partly_counter += 1



				promise_details["title"] = promise[3]
				category_promises_list.append(promise_details)

			category_details["items"] = category_promises_list

			promises_list.append(category_details)

		print("V1 benchmark: setting settables", datetime.datetime.now())
		start_date = selected_politician[6]
		end_date = datetime.datetime(2024,10,1)
		today_date = datetime.datetime.now()
		passed_months = diff_month(start_date,today_date)
		remaining_months = -1*(diff_month(today_date,end_date))-1
		total_days = (end_date - start_date).days
		passed_days = (today_date - start_date).days
		days_percentage = (passed_days / total_days) * 100
		success_percentage = (success_counter / promise_counter) * 100
		pending_percentage = (pending_counter / promise_counter) * 100
		partly_percentage = (partly_counter / promise_counter) * 100

		page_properties = {"name" : selected_politician[1], 
					   "location" : selected_politician[2], 
					   "title" : selected_politician[3], 
					   "start_date" : start_date.strftime("%Y. %B. %-d."), 
					   "program_name" : selected_politician[5], 
					   "notes" : selected_politician[4],
					   "days_percentage" : "%.1f" % days_percentage,
					   "promise_counter" : promise_counter,
					   "success_counter" : success_counter,
					   "success_percentage" : "%.1f" % success_percentage,
					   "pending_counter" : pending_counter,
					   "partly_counter" : partly_counter,
					   "pending_percentage" : "%.1f" % pending_percentage,
					   "partly_percentage" : "%.1f" % partly_percentage,
					   "remaining_months" : remaining_months,
					   "og-image" : "/static/images/" + politician + ".png",
					   "og-title" : selected_politician[1] + " " + str(promise_counter) + " ígéretéből eddig " + str(success_counter) + " teljesült, " + str(pending_counter) + " folyamatban.",
					   "og-description" : "ÍgéretFigyelő.hu by KEMO | " + selected_politician[1],
					   "promises_list" : promises_list,
					   "sidebar" : {"title" : selected_politician[1] + " névjegye", "content": {"newsfeed" : latest_news_formatted}},
					   "status_message" : status_message}

		print("V1 benchmark: returning html template", datetime.datetime.now())
		print("V1 benchmark: total time", datetime.datetime.now() - benchmark_start_time)
		return render_template("igeretfigyelo.html", selected_promise_id = selected_promise_id, static_content = "static content", page_properties = page_properties, permalink = politician)


@app.route("/process_submission")
def submission_processor():
	dbc = DatabaseOperations()

	submission_id = str(request.args.get("submission_id"))
	politician = request.args.get("politician_id")

	permitted_users = dict()
	email_list = list()
	
	dbc.cursor.execute("SELECT user_id FROM user_permissions WHERE politician_id = (%s)", [politician])
	moderators = dbc.cursor.fetchall()
	
	for m in moderators:
		permitted_users[m[0]] = dict()
	
	dbc.cursor.execute("SELECT id FROM users WHERE permissions = 'full'")
	admins = dbc.cursor.fetchall()
	
	for a in admins:
		permitted_users[a[0]]= dict()
	
	for user_id in permitted_users:
		dbc.cursor.execute("SELECT email FROM users WHERE id = (%s)", [user_id])
		permitted_users[user_id]["email"] = dbc.cursor.fetchone()[0]
		email_list.append(permitted_users[user_id]["email"])

	extra_options = dict()

	if len(email_list) > 0:
		extra_options["email_list"] = email_list
	

	dbc.cursor.execute("SELECT * FROM submissions WHERE id = (%s)", [submission_id])
	current_submission = dbc.cursor.fetchone()

	keys = ["article_date", "submitter_ip", "url", "source_name", "article_title", "politician_id", "promise_id", "submitted_at", "submitted_by", "id", "confirm_status", "confirmed_by", "suggested_status", "not_valid_items"]

	submission_parameters = dict()

	for counter, item in enumerate(current_submission):
		submission_parameters[keys[counter]] = item

	mail_body = dict()

	if not submission_parameters["submitted_by"]:
		submission_parameters["submitted_by"] = "ismeretlen"
	
	if submission_parameters["promise_id"] == 0:
		submission_parameters["promise_id"] = "nincs megadva"

	mail_body["html"] = '''
	<p><b>{} felhasználó {} IP-címről új cikket küldött be az Ígéretfigyelőn {}-kor\n</b><br>
	<p><b>Politikus:</b> {}, <b>ígéret sorszáma:</b> {}<br>
	<p><b>Cikk:</b> {} - <a href={}>{}</a></p>
	<p><a href="http://igeretfigyelo.hu/ifadmin">cikkbeküldések kezelése</a></p>
	'''.format(str(submission_parameters['submitted_by']), submission_parameters['submitter_ip'], (datetime.datetime.now()+datetime.timedelta(hours = 2)).strftime("%Y-%m-%d %H:%M:%S"), submission_parameters['politician_id'], submission_parameters['promise_id'], submission_parameters['article_title'], submission_parameters['url'], submission_parameters['url'])
	
	mail_body["text"] = submission_parameters['submitter_ip'] + ',' + str(datetime.datetime.now()) + ',' + submission_parameters['politician_id'] + ',' + str(submission_parameters['promise_id']) + ',' + submission_parameters['url'] +',' + submission_parameters['article_title']

	send_email("Ígéretfigyelő: új cikkbeküldés", mail_body, extra_options)

	return redirect("/" + politician + "?submission_success=" + str(submission_parameters['id']))


def validate_submission(submission_data):
	dbc = DatabaseOperations()

	validation_errors = dict()

	# print("URL TESZT", submission_data["url"])

	dbc.cursor.execute("SELECT * FROM news_articles WHERE url = %s", [submission_data["url"]])
	test_if_existing = dbc.cursor.fetchone()
	print(test_if_existing)
	try:
		if len(test_if_existing) != 0:
			validation_errors["vótmá"] = True
	except:
		pass

	if not submission_data["title"] or "cím beolvasása nem" in submission_data["title"] or submission_data["title"] == "None":
		validation_errors["title"] = True

	try:
		date_check = datetime.datetime.strptime(submission_data["date"], "%Y-%m-%d")
	except:
		validation_errors["date"] = True

	if submission_data["date"] == "1982-01-18":
		validation_errors["date"] = True

	if submission_data["source-name"] == "":
		validation_errors["source_name"] = True

	try:
		pid_check = int(submission_data["promise"])
	except:
		validation_errors["promise_id"] = True

	if int(submission_data["promise"]) == 0:
		if submission_data["new-promise"] == "":
			validation_errors["new_promise_title"] = True

	if "discard" in submission_data["save-action"]:
		pass
	elif "save" in submission_data["save-action"]:
		pass
	else:
		validation_errors["save_action"] = True

	return validation_errors



@app.route("/manage_submissions", methods = ["POST"])
def save_changes():
	dbc = DatabaseOperations()
	f = request.form
	submissions = dict()

	MAIN_SETTINGS["DEBUG_OPTIONS"] = False
	edit_feedback = {"saved" : "", "deleted" : "", "error" : ""}

	try:
		finalize_check = str(f['finalize-check'])
		finalize_check = True
	except:
		finalize_check = False



	compareable_values = {0: "date", 1: "url", 2: "source-name", 3: "title", 4: "promise", 5: "new-promise-status", 6: "save-action"}
	db_col_names =  {0: "article_date", 1: "url", 2: "source_name", 3: "article_title", 4: "promise_id", 5: "suggested_status", 6: "confirm_status"}

	# nem összekeverendő a suggested_status a confirm_statussal: a confirm a sub elfogadottságának státusza, a suggested pedig az ígéreté

	for key in f.keys():
		for value in f.getlist(key):
			try:
				key, sub_counter = key.split("_")
				insert = True
			except:
				insert = False

			if insert:
				if not sub_counter in submissions:
					submissions[sub_counter] = dict()
				submissions[sub_counter][key] = value
			# itt lenne a legjobb ellenőrizni, hogy véglegesíthető-e: van-e cím, dátum, action, stb - ha igen, akkor a submissions[sub_counter]["finalizable"] True lesz
			# ha be van pipálva a véglegesítés, akkor csak a véglegesíthetőknél kerül confirmed_save vagy _delete a státuszba, a többiek kapnak egy flag-et,
			# és pipa esetén a műveletvégi redirect az /ifadmin?check_finalization argumenttel megy, és ez a debugmódhoz hasonlóan mutatja, hogy finalizálható-e
			# így elég csak egyszer, ott ellenőrizni a véglegesíthetőséget (bár talán itt is kell a DB-be írás előtt, mert a formon megváltozhat - ezen ne múljék.

	for sub_count in submissions:

		new_submission_details = submissions[sub_count]
		sub_id = submissions[sub_count]["sub-id"]

		dbc.cursor.execute("SELECT DATE(article_date), url, source_name, article_title, promise_id, suggested_status, confirm_status, not_valid_items, * FROM submissions WHERE id = (%s)", [str(int(sub_id))])
		original_submission_details = dbc.cursor.fetchone()

		differences = dict()
		validation_errors = dict()



		# itt kezdődik az a loop, ami az egyes oszlopokat mahinálja.
		# nekünk a confirm dolgokat ez UTÁN kell elkezdeni ... ->
		for original_value_id, modified_value_id in compareable_values.items():

			orig = str(original_submission_details[original_value_id])
			modif = str(new_submission_details[modified_value_id])
			db_col_name = db_col_names[original_value_id]

			if db_col_name == "article_date" and orig == "1982-01-18":

				if not modif:
					modif = orig

			if db_col_name == "promise_id" and int(orig) == 0:
				new_promise_title = new_submission_details["new-promise"]
				if new_promise_title:
					dbc.cursor.execute("SELECT * FROM promise_categories WHERE politician_id = (%s) ORDER BY category_id DESC LIMIT 1", [new_submission_details["politician-id"]])
					last_promise_category = dbc.cursor.fetchone()

					dbc.cursor.execute("SELECT * FROM promises WHERE politician_id = (%s) ORDER BY id DESC LIMIT 1", [new_submission_details["politician-id"]])
					last_promise = dbc.cursor.fetchone()

					last_promise_category_id = int(last_promise_category[1])
					last_promise_id = last_promise[0]

					dbc.cursor.execute("INSERT INTO promises VALUES (%s, %s, %s, %s, %s)", [str(int(last_promise_id)+1), new_submission_details["politician-id"], str(last_promise_category_id), new_promise_title, "draft"])
					# itt beinzertáljuk a promise-ok közé újnak, de csak mint draft

					dbc.cursor.execute("UPDATE submissions SET promise_id = (%s) WHERE id = (%s)", [str(int(last_promise_id)+1), sub_id])
					# a submission promise_id-jét is át kell tenni az újra itt, mert ez már tkp nem új, de mégis

					modif = str(last_promise_id+1)


			if db_col_name == "confirm_status":

				# itt lesz az, hogy ha be van pipálva a véglegesítés, akkor elágazunk: mark_save illetve confirm_save
				# if kibaszott pipa oda van téve: save_type = "confirm" else: "mark"
				# itt most próbaképp legyen egy False:
	
				
	
				# innentől az éles elágazás:

				# de előtte szétspliteljük hogy mi a fasz. Ha None vagy null vagy lófasz akkor legyen lófasz és írjuk felül az újjal.

				try:
					orig_confirm_level, orig_confirm_status = orig.split("_")

				except:
					pass

				# itt ez mindenképp kell az oszlopozáson belül is, hiszen az error_list is egy oszlop, amit módosítani akarunk

				validation_errors = validate_submission(submissions[sub_count])
				
				if bool(validation_errors) == False:
					error_list = list()
					for error in validation_errors:
						error_list.append(error)
	
					error_list_string = str(error_list).replace("[", "{").replace("]", "}").replace('"', "'")
				else:
					error_list_string = "{}"
				
				dbc.cursor.execute("UPDATE submissions SET not_valid_items = %s WHERE id = %s", [str(error_list_string), str(sub_id)])

				
	
				if "save" in modif or "discard" in modif or modif == "":
					if not finalize_check:
						modif = "marked_" + modif
					
					else:
						print("finelize check")
						if "save" in modif:
							if bool(validation_errors) == False:
								modif = "confirmed_save"
								edit_feedback["saved"] += str(sub_id) + "_"
							else:
								modif = "marked_save"
						
						elif "discard" in modif:
							modif = "confirmed_discard"
							edit_feedback["deleted"] += str(sub_id) + "_"
						else:
							modif = ""
							edit_feedback["error"] += str(sub_id) + "_"


				else:
					modif = ""

				# bármi is a döntés, be kell juttatni a tábla "confirmed_by" oszlopába a júzert

				# a for sub in submissions_list: - 	current = dict() dictbe bele kell majd tenni, 
				# és ott dől el, hogy az adott júzernek megjelenjen-e a sub kártyája
				# vagyis benne legyen-e a dictben

				# és akkor az admin.html-ben ezzel egyáltalán nem kell már szarozni

			if orig != modif or db_col_name == "confirm_status":
				
				dbc.cursor.execute("UPDATE submissions SET %s = %s WHERE id = %s", [AsIs(db_col_name), modif, sub_id])

				if db_col_name == "confirm_status":
					dbc.cursor.execute("UPDATE submissions SET confirmed_by = %s WHERE id = %s", [str(session["user_id"]), sub_id])

				dbc.cursor.execute("INSERT INTO submissions_activity_log VALUES (%s, %s, %s, %s, %s, %s)", [str(datetime.datetime.now()), session["user_id"], str(sub_id), db_col_name, str(orig), str(modif)])

			else:
				pass # print("- - - ORIG:", orig, " -> MODIF", modif)



				# ----> ez kezdődik itt		
						
			# DEBUG: return Markup(str(submissions[sub_count]) + "<hr>" + str(validation_errors) + "<hr>Validation errors: " + str(bool(validation_errors))
			# confirmed csak akkor lehet, ha validált
			

		validation_errors = validate_submission(submissions[sub_count])

		if bool(validation_errors) == False:

				# ha admin a session user: itt kerül be a news_articles table-be a cikk, valamint ha az ígéret új, akkor a promises table-ban a "draft" flag eltűnik
				# submissions[sub_count] tartalmazza az összes adatot, ezután az if után a confirmedet is, szóval itt már van mit a DB-be tenni, nem kell megvárni az orig==modif-et
				# viszont ekkor érdemes az origot meg a modifot is valamire megváltoztatni, hogy ne legyen egyenlő
				# --> EZ HÜLYESÉG! Hiszen a fenti ifek még sorszámot adnak a new promise-nak meg ilyesmi --> és ez a if db_col_name == "confirm_status": legyen az első az itteni ifek közül, hogy a többit akkor már ne is nézz
				# PIPA: még egy fontos dolog: ha új az ígéret, azt is validálni kell, hogy van-e címe

				# ha admin, ha nem: ha nincs validation error, akkor a DB-ben le kell szedni

			if session['user_type'] == "full" and finalize_check:

					# itt írjuk a news_articlesbe az új cikket,

					# illetve az ígéretről levesszük a "draft" flag-et
				if "new-promise" in submissions[sub_count]:
					dbc.cursor.execute("UPDATE promises SET custom_options = %s WHERE id = %s and politician_id = %s", [None, submissions[sub_count]["promise"], submissions[sub_count]["politician-id"]])
						
				print("new_submission_details: ", str(new_submission_details))
				news_insert_query_parameters = [str(new_submission_details["date"]), new_submission_details["url"], new_submission_details["source-name"], new_submission_details["title"], new_submission_details["politician-id"], new_submission_details["promise"], new_submission_details["new-promise-status"]]
				print("news_insert_query_parameters: ", news_insert_query_parameters)
				dbc.cursor.execute("INSERT INTO news_articles VALUES (%s, %s, %s, %s, %s, %s, %s)", news_insert_query_parameters)


		else:

			validation_error_strings = {"vótmá" : "ez a cikk már szerepel az adatbázisban",
										"date" : "cikk dátuma nem megfelelő",
										"title" : "cikk címe nincs megadva",
										"source_name" : "forrás neve nem megfelelő",
										"promise_id" : "új ígéret nincs megadva",
										"new_promise_title" : "új ígéret nincs megadva",
										"save_action" : "mentési művelet nincs megadva"}

			error_list = list()
			for error in validation_errors:
				error_list.append(validation_error_strings[error])

			error_list_string = str(error_list).replace("[", "{").replace("]", "}").replace('"', "'")
			dbc.cursor.execute("UPDATE submissions SET not_valid_items = %s WHERE id = %s", [str(error_list_string), str(sub_id)])




	'''
	for submission_counter, msp in submissions.items(): # msp = modified_submission_parameters, ez jön a formból
		

		print("             ", submission_counter, original_submission)

		


	'''
		# összehasonlítjuk a sub parákat a DB-ben levőkkel
		# végig iteráljuk az egyes parákat, és egy changes változóba teszünk true-t, ha valami változás van

		# VAGY

		# előbb megnézzük, van-e action, VAGY a change az actionban van

		# ha változás van

		# if changes:

			# ezután írjuk át a Submissions táblában a cuccokat

			# a mentés és a véglegesítés gombok között között egy url arg a különbség, ezt itt bekérjük, és annak megfelelően dolgozunk

			# odafigyelni: ha véglegesítést nyom a júzer, akkor lehet, hogy nincsenek változások, mert előtte mentett. A véglegesítést az "if changes" előtt, DE csak 
			# ha "action" van az F-ben

			# végül pedig ha adminok vagyunk, a változott sub bekerül a news_article táblába, a submissionből törlődik(?)
		
			# if session["user_type"] == "full":	
	
	return redirect("/ifadmin?s={}&d={}&n={}".format(edit_feedback["saved"][:-1], edit_feedback["deleted"][:-1], edit_feedback["error"][:-1]))


@app.route("/link")
def count_out_link():
	url = request.args.get("url")
	return redirect(url)

@app.route("/activity_log")
def activity_log_page():

	dbc = DatabaseOperations()

	dbc.cursor.execute("SELECT * FROM submissions_activity_log ORDER BY dt DESC LIMIT 500")
	activities = dbc.cursor.fetchall()
	return render_template("activity_log.html", activities = activities, page_properties = {"sidebar" : {"title" : "", "contents" : ""}}, static_content = "")






@app.route("/kemocloud-system-status")
def kcss_page():

	machines = ["Rescueboat", "NASi", "rpi_two", "rpi_one", "Soul2K10", "Bastion"]


	dbc = DatabaseOperations()
	if "heartbeat" in request.args:
		base = request.args.get("base")
		machine = request.args.get("machine")
		dt = datetime.datetime.utcnow()
		headers_list = request.headers.getlist("X-Forwarded-For")
		ip = headers_list[0] + " (HL)"if headers_list else request.remote_addr + " (R.R_A)"
		if "notes" in request.args:
			notes = request.args.get("notes")

			dbc.cursor.execute("INSERT INTO kemocloud_system_status VALUES (%s, %s, %s, %s, %s)", [dt, base, machine, ip, notes])
		else:
			dbc.cursor.execute("INSERT INTO kemocloud_system_status VALUES (%s, %s, %s, %s)", [dt, base, machine, ip])

		return "ok"
	
	else:

		if not "machine" in request.args:
			dbc.cursor.execute("SELECT * FROM kemocloud_system_status ORDER BY dt DESC limit 100")
		else:
			dbc.cursor.execute("SELECT * FROM kemocloud_system_status WHERE machine=(%s) ORDER BY dt DESC limit 100", [request.args.get("machine")])

		if "notes" in request.args:
			dbc.cursor.execute("SELECT * FROM kemocloud_system_status WHERE notes IS NOT NULL ORDER BY dt DESC limit 100")

		last_100_system_reports = dbc.cursor.fetchall()

		page_html = '<html><head><link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous"></head><body><h2 style="text-align: center; margin-top: 25px; margin-bottom: 10px;">'

		for m in machines:
			dbc.cursor.execute("SELECT * FROM kemocloud_system_status WHERE machine=(%s) ORDER BY dt DESC limit 1", [m])
			last_report = dbc.cursor.fetchone()
			
			try:
				last_online = last_report[0]
				delta = datetime.datetime.utcnow() - last_online
				
				if delta.seconds < 70:
					delta = ""
					div_class = "badge badge-success"
				elif delta.seconds < 3600:
					delta = "(" + str(int(delta.seconds/60)) + " m)"
					div_class = "badge badge-warning"
				else:
					delta = "(" + str(int(delta.seconds/3600)) + " h)"
					div_class = "badge badge-danger"

			except:
				delta = "X"
				div_class = "badge badge-danger"
			
			link_string = '<span class="{}" style="margin-left: 5px; margin-right: 5px;"><a style="color: #ffffff !important;" href="/kemocloud-system-status?machine={}">{} {}</a></span>'.format(div_class, m, m, delta)
			page_html += link_string

		page_html += '</h2><p style="text-align: center; font-size: 16px; margin-bottom: 16px;">Filter notes only: <a href="/kemocloud-system-status">off</a> | <a href="/kemocloud-system-status?notes=filter">on</a></p><table class="table">'
		for r in last_100_system_reports:
			if r[4]:
				r_4 = r[4]
			else:
				r_4 = ""
			page_html += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format(r[0].replace(tzinfo=datetime.timezone.utc).astimezone(tz=None), r[1], r[2], r[3], r_4)

		page_html += '''
		</table><script src="https://code.jquery.com/jquery-3.3.1.slim.min.js" integrity="sha384-q8i/X+965DzO0rT7abK41JStQIAqVgRVzpbzo5smXKp4YfRvH+8abtTE1Pi6jizo" crossorigin="anonymous"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.14.3/umd/popper.min.js" integrity="sha384-ZMP7rVo3mIykV+2+9J3UJ46jBk0WLaUAdn689aCwoqbBJiSnjAK/l8WvCWPIPm49" crossorigin="anonymous"></script>
    <script src="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/js/bootstrap.min.js" integrity="sha384-ChfqqxuZUCnJSK3+MXmPNIyE6ZbWh2IMqE241rYiqJxyMiZ6OW/JmZQ5stwEULTy" crossorigin="anonymous"></script>
    </body></html>'''

		return Markup(page_html)





if __name__ == "__main__":
	app.config['SERVER_NAME'] = "igeretfigyelo.hu" 
	app.run(host='127.0.0.1', port=8080)