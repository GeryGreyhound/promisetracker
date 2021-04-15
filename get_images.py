'''

Test project: get all the og-images of articles of a selected politicians' promises

'''

import requests
import shutil
import lxml
import os
import wget
from bs4 import BeautifulSoup

import new_refactored_oop_functions as promisetracker_v2


def get_image_url(article_url):
	r = requests.get(article_url)
	soup = BeautifulSoup(r.content, "lxml")
	try:
		image_url = soup.find("meta",  attrs={'property': 'og:image'})['content']
		print(image_url)
		return image_url
	except:
		return False

def get_description(article_url):
	r = requests.get(article_url)
	soup = BeautifulSoup(r.content, "lxml")
	try:
		description = soup.find("meta",  attrs={'property': 'og:description'})['content']
		return description
	except:
		return False

def download_image(image_url, filename):
	r = requests.get(image_url, stream=True)
	if r.status_code == 200:
		with open(os.path.join("article_images", filename), 'wb') as f:
			r.raw.decode_content = True
			shutil.copyfileobj(r.raw, f)
	else:
		print("DL fail 1 - r.status_code != 200")


def de_hungarize(string):
	hun_chars = {"á" : "a", "é" : "e", "í" : "i", "ó" : "o", "ö" : "o", "ő" : "o", "ú" : "u", "ü" : "u", "ű" : "u"}
	for c in hun_chars:
		if c in string:
			string = string.replace(c, hun_chars[c])

	return string


if __name__ == "__main__":
	
	test_politician = promisetracker_v2.Politician('karacsonygergely')
	
	category_list = test_politician.promise_list.promise_categories
	
	for cat in category_list:
	
		promises = cat["promise_list"] # itt látszik a hiba, amiért MINDENNEK objectnek kell lennie, nem object listjébe rakott dictbe rakott object, mert ez így fos
	
		for p in promises:
	
			article_list = p.articles
	
			for a in article_list:
	
				image_url = get_image_url(a.url)
				description = get_description(a.url)
	
				if image_url:
	
					article_date = str(a.date)[:10]
					article_source_name = de_hungarize(a.source_name.lower())
					image_extension = list(image_url.split("."))[-1]
					filename = "{}_{}.{}".format(article_source_name, article_date, image_extension)
	
					try:
						download_image(image_url, filename)
					except Exception as e:
						print("DL fail 2:", str(e.args))

				else:
					print("DL fail 3: no image")

				if description:
					print(description)
				else:
					print("NO description")


