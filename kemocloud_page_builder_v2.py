DEFAULT_VALUES = {
	"page_title" : "KEMOCloud Pagebuilder v2.0 demo",
	"page_language" : "hu",
	"head_imports" : 
		['<link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.1.3/css/bootstrap.min.css" integrity="sha384-MCw98/SFnGE8fJT3GXwEOngsV7Zt27NXFoaoApmYm81iuXoPkFOJwJ8ERdknLPMO" crossorigin="anonymous">',
		 '<link href="/static/css/blog-home.css" rel="stylesheet">'
		],
	"body_end_imports" : 
		['<script src="https://code.jquery.com/jquery-3.2.1.slim.min.js" integrity="sha384-KJ3o2DKtIkvYIK3UENzmM7KCkRr/rE9/Qpg6aAZGJwFDMVNA/GpGFF93hXpG5KkN" crossorigin="anonymous"></script>',
		 '<script src="https://cdnjs.cloudflare.com/ajax/libs/popper.js/1.12.9/umd/popper.min.js" integrity="sha384-ApNbgh9B+Y1QKtv3Rn7W3mgPxhU9K/ScQsAP7hUibX39j7fakFPskvXusvfa0b4Q" crossorigin="anonymous"></script>',
		 '<script src="https://maxcdn.bootstrapcdn.com/bootstrap/4.0.0/js/bootstrap.min.js" integrity="sha384-JZR6Spejh4U02d8jOt6vLEHfe/JQGiRRSQQxSfFWpi1MquVdAyjUar5+76PVCmYl" crossorigin="anonymous"></script>'
		 ],
	"custom_css" : '''
	<style>
	.promise_list_item_title {
	cursor: pointer;
	position: relative;
	display: table;
	}
	</style>
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

	"featured_banner" : '<p>Featured banner placeholder</p>',
	"footer_text" : 'PromiseTracker V2.21a 2019-2021 &copy Tomanovics Gergely @ Kreatív Ellenállás Mozgalom<br>Made with KEMOCloud Page Builder 2021<br>Except where otherwise noted, this website is licensed under a <a rel="license" href="http://creativecommons.org/licenses/by/3.0/deed.en_US">Creative Commons Attribution 3.0 Unported License</a>.'

	}

# legyen egy page_specific_values global is
# ha ebben van egy paraméter, az felülírja a defaultot
# pl if "page_title" in "PAGE_SPECIFIC_VALUES" -> DEFAULT_VALUES["page_title"] = PAGE_SPECIFIC_VALUES["page_title"]
# persze iterálva for looppal:

PAGE_SPECIFIC_VALUES = {
	"page_title" : "Ígéretfigyelő",
	"x" : "y"
	}



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
		self.og_properties = "OG1\nOG2\nOG3"
		self.content_layout = "right_sidebar"
		self.featured_banner = DEFAULT_VALUES["featured_banner"]
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

	def generate_navbar(self, items):
		navbar_items_html = ""
		
		for item in items:
			if item["type"] == "link":
				item_html = HtmlElements.navbar_link.format(link_target = item["target"], link_title = item["title"])

			elif item["type"] == "dropdown":
				sub_items_html = ""

				for dropdown_item in item["items"]:
					sub_items_html += HtmlElements.navbar_dropdown_item.format(link_target = dropdown_item["target"], link_title = dropdown_item["title"])

				item_html = HtmlElements.navbar_dropdown.format(dropdown_title = item["title"], dropdown_items = sub_items_html)

			navbar_items_html += item_html + "\n"

		self.navbar = HtmlElements.navbar_base.format(page_title = self.page_title, navbar_items = navbar_items_html)

	def generate_sidebar(self, items):
		self.sidebar = ""

		for item in items:
			print(item)
			item_html = HtmlElements.sidebar_widget.format(widget_title = item["title"], widget_content = item["content"])
			self.sidebar += item_html



		



class HtmlElements:

	page_basics = '''
	<html lang={page_language}>
	<head>
	<title>{page_title}</title>

	{google_analytics_script}
	{head_imports}
	{og_properties}

	</head>
	
	<body>

	<div class="container">

	{navbar}
	{featured_banner}
	{content}
	{footer}
	{body_end_imports}

	</div>
	
	</body>
	</html>
	'''


	content_layouts = {"full_width" : "",
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

	navbar_base = '''
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

	navbar_dropdown_item = '''
	<a class="dropdown-item" href="{link_target}">{link_title}</a>\n
	'''

	sidebar_widget = '''
	<div class = "card">
	<h5 class = card-header>{widget_title}</h5>
    <div class="card-body">
    <p>{widget_content}</p>
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








