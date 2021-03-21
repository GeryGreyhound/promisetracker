from new_refactored_oop_functions import *

import csv

'''



with open ("politician_fulop_zsolt_szentendre_pm.csv", "r") as csvfile:
	reader = csv.reader(csvfile, delimiter = ";")

	politician_name = "fulopzsolt"
	category_counter = 0
	item_counter = 0

	for line in reader:

		line[1] = line[1].replace("\t", "")

		for x in range(175, 0, -1):
			if str(x) + ". " in line[1]:
				line[1] = line[1].replace(str(x) + ". ", "")

		if "info" in line[0]:
			print("Info:", line)
			sql_command = None
	
		elif line[0] == "cat":
			category_counter += 1
			sql_command = "INSERT INTO promise_categories VALUES (%s, %s, %s);"
			sql_data = (politician_name, category_counter, line[1])
	
		elif line[0] == "item":
			item_counter += 1
			promise_title = line[1]
			sql_command = "INSERT INTO promises VALUES (%s, %s, %s, %s, %s, %s);"
			sql_data = (item_counter, politician_name, category_counter, promise_title, "", [])

			if len(line) > 2:
				
				article = Article(line[2])
				suggested_status = line[3]
				
				article.get_meta_data()
				article.add_to_submissions(politician_name, item_counter, "CSV importer robot", "localhost", datetime.datetime.now(), suggested_status)

			
			try:
				pass
				# print(sql_command, sql_data)
				# dbc.cursor.execute(sql_command, sql_data)
			except:
				pass

'''

'''
teszt_art = Article("https://szentendre.hu/wp-content/uploads/2020/09/98-hoz-melleklet-KULT-KFT_%C3%9Czleti-Terv_2020.-%C3%A9vi-M%C3%B3dos%C3%ADtott_20200820.pdf")
teszt_art.get_meta_data()
teszt_art.add_to_submissions("shrekszilard", 3, "CSV importer robot", "localhost", datetime.datetime.now(), "pending")

'''

stop_watch(s)

teszt_pol = Politician("karacsonygergely")
if teszt_pol.existent:
	print("ED:", teszt_pol.end_date)
else:
	print("Politician does not exist")
'''


for category in teszt_pol.promise_list.promise_categories:
	print(">>>> ", category["name"])

	for promise in category["promise_list"]:

		if promise.status == "pending":

			print(promise.id, promise.name, promise.status)
			if len(promise.articles) > 0:
				for art in promise.articles:
					print ("|", art.title)
					# print(art.__dict__)
'''

print("----\n",teszt_pol.promise_list.status_counters)

stop_watch(e)



'''

teszt_pg = Page()
teszt_pg.og_title = "testing OOP HTML generator - changed title"
teszt_pg.og_description = "Here comes the changed description"

teszt_pg.construct_html()

with open ("teszt.html", "w") as htmlfile:
	htmlfile.write(teszt_pg.html_page)


'''