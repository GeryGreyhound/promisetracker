DEFAULT_VALUES = {
	"page_title" : "KEMOCloud Pagebuilder v2.0 demo",
	"page_language" : "hu",
	"head_imports" : ''' 
		<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">
		<link href="/static/css/blog-home.css" rel="stylesheet">
		''',
	"body_end_imports" : '''
		<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>
		<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>
		<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>
		''',
	"custom_css" : '''

	.sidebar_widget {
	margin-bottom: 15px;	
	}

	.top_banner {
	background-color: #eeeeee;
	font-size: 30px;
	font-weight: 100;
	text-align: center;
	padding: 15px;
	margin-bottom: 15px;
	}

	.menu-dropdown-language-selector {
	width: 24px;
	height: auto;
	}

	.navbar-logo {
	width:40px;
	height: auto;
	}

	.navbar-page-name {
	font-size: 32px;
	font-weight: 100;
	}

	'''
	,
	"navbar_items" : [
		{"type" : "link", "target" : "demo_target", "title" : "Demo link 1"},
		{"type" : "link", "target" : "demo_target_2", "title" : "Demo link 2"},
		{"type" : "dropdown", "title" : "Demo dropdown", "items" : [{"target" : "dd_1", "title" : "Dropdown demo 1"}, {"target" : "dd_2", "title" : "Dropdown demo 2"}]}
					],
	"sidebar_widgets" : [{"title" : "Demo widget 1", "content" : "Lorem Ipsum is simply dummy text of the printing and typesetting industry. Lorem Ipsum has been the industry's standard dummy text ever since the 1500s, when an unknown printer took a galley of type and scrambled it to make a type specimen book. <a href=https://www.lipsum.com/>read more</a>"},
						 {"title" : "Demo widget 2", "content" : "Widget 2 contents"}
						 ],


	"top_banner" : '<div class="top_banner"><p>Top banner placeholder</p></div>',
	"footer_text" : 'PromiseTracker V2.21a 2019-2021 &copy Tomanovics Gergely @ Kreatív Ellenállás Mozgalom<br>Made with KEMOCloud Page Builder 2021<br>Except where otherwise noted, this website is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/3.0/deed.en_US">Creative Commons Attribution 3.0 Unported License</a>.'

	}

# legyen egy page_specific_values global is
# ha ebben van egy paraméter, az felülírja a defaultot
# pl if "page_title" in "PAGE_SPECIFIC_VALUES" -> DEFAULT_VALUES["page_title"] = PAGE_SPECIFIC_VALUES["page_title"]
# persze iterálva for looppal:


'''
ezeket inkább a routesben adjuk meg, itt fölösleges
PAGE_SPECIFIC_VALUES = {
	"page_title" : "Ígéretfigyelő",
	"x" : "y"
	}
'''


class Page:
	def __init__(self):
		# to-do: kéne valami page_id ami segítségével aktívra állítja a navbar megfelelő menüpontját
		# self.page_id = ???, if self.page_id = self.active_page_id: self.active = True
		self.page_title = DEFAULT_VALUES["page_title"]
		self.page_language = DEFAULT_VALUES["page_language"]
		self.head_imports = DEFAULT_VALUES["head_imports"] # ezek listek, hogy a class instance-hez Object.head_imports.append('<script src="..."') formában hozzá lehessen bármit adni
		self.body_end_imports = DEFAULT_VALUES["body_end_imports"]
		self.custom_css = DEFAULT_VALUES["custom_css"] # ez kivételesen nem list, hanem string, ehhez += operátorral kell hozzáadni, ha hozzá kell bármit
		self.navbar_items = DEFAULT_VALUES["navbar_items"]
		self.sidebar_widgets = DEFAULT_VALUES["sidebar_widgets"]
		self.google_analytics_id = 'UA-85693466-4'
		self.meta_values = ""
		self.content_layout = "right_sidebar"
		self.top_banner = DEFAULT_VALUES["top_banner"]
		self.footer_text = DEFAULT_VALUES["footer_text"]

		self.main_content = '<h1>Árvíztűrő tükörfúrógép</h1><hr><p class="lead">Lorem Ipsum ecet retek</p>'

	def assemble_html_parts(self):

		# ami listából áll, azt muszáj így létrehozni

		self.generate_navbar(self.navbar_items)  # vagyis generate_navbar(items)? Meglátjuk, ez hogy jó
		self.generate_sidebar(self.sidebar_widgets)

		# self.generate_page_body(self.innen_nem tudom fáradt vagyok de gecire)  - ez lehet h nem is kell, csak a content_layout
		# sidebar widgetekig elvileg OK a dolog

		# self generate_html oszt belehajígálni az alábbiakat? 

		self.content = HtmlElements.content_layouts[self.content_layout].format(main_content = self.main_content, sidebar = self.sidebar)
		self.footer = HtmlElements.footer.format(footer_text = self.footer_text)

		# self.page_body = HtmlElements.page_body.format(**self.__dict__)
		
		self.google_analytics_script = HtmlElements.google_analytics_script.format(**self.__dict__)
		
		self.final_html = HtmlElements.page_basics.format(**self.__dict__)

	def generate_navbar(self, items, split = True):
		navbar_items_html = ""
		navbar_items_split_part = ""
		
		for item in items:
			if item["type"] == "link":
				item_html = HtmlElements.navbar_link.format(link_target = item["target"], link_title = item["title"])
				split_position = "left"

			elif item["type"] == "dropdown":
				sub_items_html = ""

				for dropdown_item in item["items"]:
					sub_items_html += HtmlElements.navbar_dropdown_item.format(link_target = dropdown_item["target"], link_title = dropdown_item["title"])

				item_html = HtmlElements.navbar_dropdown.format(dropdown_title = item["title"], dropdown_items = sub_items_html)
				split_position = "left"

			elif item["type"] == "language_switch":
				sub_items_html = ""

				for dropdown_item in item["items"]:
					if dropdown_item != self.page_language:
						sub_items_html += HtmlElements.navbar_dropdown_item.format(link_target = "/?lang={}".format(dropdown_item), link_title = '<img class="menu-dropdown-language-selector" src="/static/images/{}.png">'.format(dropdown_item))

				item_html = HtmlElements.navbar_dropdown.format(dropdown_title = '<img class="menu-dropdown-language-selector" src="/static/images/{}.png">'.format(self.page_language), dropdown_items = sub_items_html)
				split_position = "right"

			if split == True:
				if split_position == "left":
					navbar_items_html += item_html + "\n"
				elif split_position == "right":
					navbar_items_split_part += item_html 
				self.navbar = HtmlElements.navbar_2sided.format(page_title = self.page_title, navbar_items_left = navbar_items_html, navbar_items_right = navbar_items_split_part)

			else:
				navbar_items_html += item_html + "\n"
				self.navbar = HtmlElements.navbar.format(page_title = self.page_title, navbar_items = navbar_items_html)
		

	def generate_sidebar(self, items):
		self.sidebar = ""

		for item in items:
			item_html = HtmlElements.sidebar_widget.format(widget_title = item["title"], widget_content = item["content"])
			self.sidebar += item_html




		



class HtmlElements:

	page_basics = '''
	<html lang={page_language}>
	<head>
	<title>{page_title}</title>

	{google_analytics_script}
	{head_imports}
	{meta_values}
	
	<style>
	{custom_css}
	</style>
	</head>
	
	<body>

	<div class="container">

	{navbar}
	{top_banner}
	{content}
	{footer}
	{body_end_imports}

	</div>
	
	</body>
	</html>
	'''


	content_layouts = {
	"full_width" : '''
	<div class="row">
	{main_content}
	</div>
	''',
	"right_sidebar" : '''
	<div class="row">
	<div class="col-md-8">
	{main_content}
	</div>

	<div class="col-md-4">
	{sidebar}
	</div>
	</div>
	'''
	}

	google_analytics_script = '''
	<script async src="https://www.googletagmanager.com/gtag/js?id={google_analytics_id}"></script>
	<script>
  		window.dataLayer = window.dataLayer || [];
  		function gtag(){{dataLayer.push(arguments);}}
  		gtag('js', new Date());

  		gtag('config', '{google_analytics_id}');
	</script>
	'''

	meta_values = '''
	<meta charset="utf-8">
  	<meta name="viewport" content="width=device-width, initial-scale=1, shrink-to-fit=no">
  	<meta name="description" content="{meta_description}">
  	<meta name="author" content="{meta_author}">
	<meta property="og:title" content="{og_title}" />
  	<meta property="og:description" content="{og_description}" />
  	<meta property="og:image" content="{og_image}" />
	'''

	navbar = '''
	<nav class="navbar navbar-expand-lg navbar-dark bg-dark fixed-top">
    	<div class="container">
    	<a class="navbar-brand" href="/">{page_title}</a>
  		<button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarSupportedContent" aria-controls="navbarSupportedContent" aria-expanded="false" aria-label="Toggle navigation">
    	<span class="navbar-toggler-icon"></span>
  		</button>

  		<div class="collapse navbar-collapse" id="navbarSupportedContent">
    	<ul class="navbar-nav mr-auto">
      	
    	{navbar_items}

     	</ul>
  		</div>
	</nav>

	'''

	navbar_2sided = '''
	
	<nav class="navbar navbar-expand-md navbar-light bg-light fixed-top">
	<div class="container">
    <a class="navbar-brand" href="/">{page_title}</a>
    <button class="navbar-toggler" type="button" data-toggle="collapse" data-target="#navbarNav">
        <span class="navbar-toggler-icon"></span>
    </button>
    <div class="collapse navbar-collapse" id="navbarNav">
        <ul class="navbar-nav mr-auto">
			{navbar_items_left}
        </ul>
        <ul class="navbar-nav">
			{navbar_items_right}
        </ul>
    </div>
</div>
</nav>

	'''

	navbar_link = '''
	<li class="nav-item">
    <a class="nav-link" href="{link_target}">{link_title}</a>
    </li>
	'''

	navbar_dropdown = '''
	<li class="nav-item dropdown">
    <a class="nav-link dropdown-toggle" href="#" id="navbarDropdown" role="button" data-toggle="dropdown" aria-haspopup="true" aria-expanded="false">
    {dropdown_title}
    </a>
        
        <div class="dropdown-menu" aria-labelledby="navbarDropdown">
        {dropdown_items}
        </div>
      	</li>
	'''

	navbar_language_selector = '''
	'''

	navbar_dropdown_item = '''
	<a class="dropdown-item" href="{link_target}">{link_title}</a>\n
	'''

	sidebar_widget = '''
	<div class = "sidebar_widget">
	<div class = "card">
	<h5 class = card-header>{widget_title}</h5>
    <div class="card-body">
    <p>{widget_content}</p>
    </div>
    </div>
    </div>

	'''

	footer = '''
	<footer class="py-5 bg-dark">
    <div class="container">
    <p class="m-0 text-center text-white">{footer_text}</a></p>
    </div>
  	</footer>
	'''


class PromisetrackerAddOn:
	custom_css = '''
	.promise_list_item_title {
	cursor: pointer;
	position: relative;
	display: table;
	}

	.promise_list_item_news_badge {display:table-cell}
	"promise_list_item_status" : "display:table-cell"
	"promise_list_item_details" : "display: none;"
	"promise_list_item_"

	'''

	custom_html = {

	"politician_page" : '''
	{image}
	{status_counters}
	{promise_list}
	'''

	"promise_category": '''
		{category_items}
		''',
	
	"promise_list_item" : '''
		<div class="promise_list_item_title" id="{id}_title" onclick="show_details({id})">
			
			{news_info_icon}
		
			<div style="display:table-cell"><span class="{status_css_class}">&nbsp;{id}&nbsp;</span></div><span style="position: relative; left: 10px; display:table-cell;">{name}</span><br></div>
	
			<div class = "promise_list_item_details" id="{id}_details" style="display: none;">
		    	<div class="card">
		    		<div class="card-header" onclick="show_details({id})">
		    		<h4><span class="{status_css_class}">{id} | {status_title}</span>{name}</h4>
				</div>
				
				<ul class="list-group list-group-flush">
					{articles_list}
		            
		            <li class="list-group-item">
		            	<form class="form-inline" name="form_{id}" method="post" action="">
		  				<div class="form-group mb-2">Hír ajánlása</div>
		  				<div class="form-group mx-sm-3 mb-2">
		    				<input type="text" class="form-control" size="40" name="submit_article_karacsonygergely_{id}" placeholder="http://index.hu/teljesult-igeretrol-szolo-cikk">
		  				</div>
		  				<button type="submit" class="btn btn-primary mb-2">Linkbeküldés</button>
						</form>
		       		</li>
		   		</ul>
			</div>
	     </div>
	
		''',

		"promise_list_news_info_icon" : '''
		<div style="display:table-cell"><span class="badge badge-light"><img alt="{article_count} kapcsolódó hír" src="static/images/newspaper.png" style="width:18px; height:auto; margin-right: 5px;"><b>{article_count}</b></span></div>
		''',

		"promise_list_item_news_list_item" : '''
		<li class="list-group-item"><a href="/link?url={url}">{title}</a><br><small>({source_name}, {date})</small></li>
		''',



	}


