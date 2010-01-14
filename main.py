import re
import cgi
import logging

import basherc

from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

# ---

class MainPage(webapp.RequestHandler):
	def get(self):
		quotes = db.GqlQuery("SELECT * FROM Quote ORDER BY date_quote DESC LIMIT 50")
		mt = basherc.MiniTemplateRenderer(self.response)
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
				
					mt = basherc.MiniTemplateRenderer(self.response)
					mt.produce_index(template_values)
					
			# we were unable to extract a key from the URI
			else:
				raise Error
				
		# if somethings happens, lets's throw a 404
		except:
			self.error(404)
			mt = basherc.MiniTemplateRenderer(self.response)
			mt.fail()

# ---

application = webapp.WSGIApplication(
									[('/', MainPage),
									(('/quote/\w+'), ViewQuote)],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()