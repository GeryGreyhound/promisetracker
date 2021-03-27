import requests
import csv

strings_csv_url = "https://docs.google.com/spreadsheets/d/e/2PACX-1vTDX5UxQbeX7FA6_3bBdiKsu-tYXX8p2pZWYuZH7TCIYRLgKaMbQeyppIlEquG1YD5NeNkw6ziJ-QvJ/pub?gid=0&single=true&output=csv"

r = requests.get(strings_csv_url)
data = r.content
with open ("config/strings.csv", "wb") as f:
	f.write(data)





'''







string_dict = dict()

with requests.Session() as s:
    download = s.get(strings_csv_url)

    decoded_content = download.content.decode('utf-8')

    cr = csv.reader(decoded_content.splitlines(), delimiter=',')
    rows = list(cr)

    for counter, row in enumerate(rows):

    	if counter == 0:

    		grouping = row[0]
    		item_id = row[1]

    		group_inner_1 = row[2]
    		group_inner_2 = row[3]
    		# innentől akárhány nyelv felvihető

    	if counter > 0:

        	string_id = row[1]

        	if row[0] != '':
        		category = row[0]
        		string_dict[category] = dict()
        	
        	string_dict[category][string_id] = {group_inner_1 : row[2], group_inner_2 : row[3]}

    for key, value in string_dict.items():
    	# for k2, v2 in value.items():
    	print(key, string_dict[key])


'''