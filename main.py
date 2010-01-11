import os
import re
import cgi
import logging

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.api import xmpp
from google.appengine.ext.webapp import template
from google.appengine.ext.webapp.util import run_wsgi_app

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
		
		path = os.path.join(os.path.dirname(__file__), 'templates/index.html')
		self.response.out.write(template.render(path, self.default_values))
	
		self.produce_footer()
		
	
# ---

class MainPage(webapp.RequestHandler):
	def get(self):
		quotes = db.GqlQuery("SELECT * FROM Quote ORDER BY date_quote DESC LIMIT 50")
		mt = MiniTemplateRenderer(self.response)
		mt.produce_index({ 'quotes': quotes })

# ---

class ViewQuote(webapp.RequestHandler):
	def get(self):
		# extract the quote's ID
		reg = re.compile('^/quote/(.+)$')
		m = reg.match(self.request.path)
		try:
			if m:
				# attempts to load a quote from the key value
				# will raise an error if the key is invalid
				quote = db.get(m.group(1))
				# if the quote was not found
				if not quote:
					raise Error
				else:
					template_values = {
						'quotes': [quote],
						'lonelymode': True
					}
				
					mt = MiniTemplateRenderer(self.response)
					mt.produce_index(template_values)
					
			# we were unable to extract a key from the URI
			else:
				raise Error
				
		# if somethings happens, it's probably the user's fault
		except:
			self.error(404)
			mt = MiniTemplateRenderer(self.response)
			mt.fail
# ---

class XMPPHandler(webapp.RequestHandler):
	def post(self):
		message = xmpp.Message(self.request.POST)
		quote = Quote()
		
		reg = re.compile('^&([^&]+)&([^&]+)&')
		m = reg.match(self.request.path)
		
		try :
			quote.author = message.sender
			quote.author_original = m.group(1)
			quote.content = m.group(2)
			quote.put()
			logging.info("[basher] message stored")
			message.reply("Thank you ! You may want to check %s now." % self.request.host_url)
		except:
			logging.info("[basher] message discarded (f=%s,c=%s)" % message.sender, message.body)
			message.reply("oops... please format your message this way : &author name&quote& . For example : &Douglas Adams&Don't Panic&")
		
# ---

application = webapp.WSGIApplication(
									[('/', MainPage),
									(('/quote/\w+'), ViewQuote),
									('/_ah/xmpp/message/chat/', XMPPHandler)],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()