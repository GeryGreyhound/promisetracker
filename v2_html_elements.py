class Promise:
	def __init__(self):
		pass

	def generate_html(self):

		html_base = HtmlElements()
		self.html_box = f(str(html_base.promise_list_item))


class HtmlElements:

	promise_list_item = '''
	<div id="{promise.id}_title" onclick="show_details({promise.id})" style="cursor: pointer; position: relative; display: table;">
		<div style="display:table-cell"><span class="badge badge-light"><img alt="3 kapcsolódó hír" src="static/images/newspaper.png" style="width:18px; height:auto; margin-right: 5px;"><b>3</b></span></div>
	
		<div style="display:table-cell"><span class="badge badge-warning">&nbsp;2&nbsp;</span></div><span style="position: relative; left: 10px; display:table-cell;">Tiborcz-adó</span><br></div>

		<div id="2_details" style="display: none;">
	    	<div class="card">
	    		<div class="card-header" onclick="show_details(2)">
	    		<h4><span class="badge badge-warning">2 | problémás</span>Tiborcz-adó</h4>
			</div>
			
			<ul class="list-group list-group-flush">
				<li class="list-group-item"><a href="/link?url=https://444.hu/2020/12/02/megtiltja-a-kormany-az-adoemelest-az-onkormanyzatoknak">Megtiltja a kormány az adóemelést az önkormányzatoknak</a><br><small>(444, 2020-12-02)</small></li>
	            <li class="list-group-item"><a href="/link?url=https://hvg.hu/gazdasag/20201013_karacsony_tiborcz_koronavirus_nagykorut_biodom_budapest_orban_eu">Karácsony Gergely: A második hullámot nem lehet politikai lózungokkal kezelni</a><br><small>(hvg.hu, 2020-10-13)</small></li>
	            <li class="list-group-item"><a href="/link?url=https://444.hu/2019/10/18/karacsony-mar-keszul-a-tiborcz-ado-jogszabalya">Karácsony: Már készül a Tiborcz-adó jogszabálya</a><br><small>(444, 2019-10-18)</small></li>
	            
	            <li class="list-group-item">
	            	<form class="form-inline" name="form_2" method="post" action="">
	  				<div class="form-group mb-2">Hír ajánlása</div>
	  				<div class="form-group mx-sm-3 mb-2">
	    				<input type="text" class="form-control" size="40" name="submit_article_karacsonygergely_2" placeholder="http://index.hu/teljesult-igeretrol-szolo-cikk">
	  				</div>
	  				<button type="submit" class="btn btn-primary mb-2">Linkbeküldés</button>
					</form>
	       		</li>
	   		</ul>
		</div>
     </div>

	'''




teszt_p = Promise()
teszt_p.id = 6

teszt_p.generate_html()

print(teszt_p.html_box)











teszt_string = "fekete {variable_1} kopog a patika {variable_2}"