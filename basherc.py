import os
import re

from google.appengine.ext import db
from google.appengine.ext.webapp import template

# ---

class Quote(db.Model):
	author = db.StringProperty()
	author_original = db.StringProperty()
	content = db.StringProperty(multiline=True)
	date_quote = db.DateTimeProperty(auto_now_add=True)
	date_record = db.DateTimeProperty(auto_now_add=True)
	
	def author_clean(self):
		try:
			reg = re.compile('^(.+@)')
			m = reg.match(self.author)
			return "%s" % m.group(1)
		except:
			return "Anonymous."
	
	def key_shortner(self):
		return self.key.id_or_name()
	
	author_clean.alters_data = False

# ---

class MiniTemplateRenderer():

	def __init__(self, response):
		self.default_values = {}
		self.response = response
		
	def produce_header(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/common/header.html')
		self.response.out.write(template.render(path, self.default_values))
			
	def produce_footer(self):
		path = os.path.join(os.path.dirname(__file__), 'templates/common/footer.html')
		self.response.out.write(template.render(path, self.default_values))
		
	def produce_index(self,template_values):
		self.produce_header()
		
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, template_values))
		
		self.produce_footer()
		
	def fail(self):
		self.produce_header()
		
		path = os.path.join(os.path.dirname(__file__), 'templates/fail.html')
		self.response.out.write(template.render(path, self.default_values))
	
		self.produce_footer()
