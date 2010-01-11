import cgi

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext.webapp.util import run_wsgi_app
from google.appengine.ext import db

# ---

class Citation(db.Model):
	author = db.UserProperty()
	author_original = db.StringProperty()
	content = db.StringProperty(multiline=True)
	date_citation = db.DateTimeProperty(auto_now_add=True)
	date_record = db.DateTimeProperty(auto_now_add=True)
	
# ---

class MicroTemplate():
	def header(self):
		
		
	def footer(self):
		

# ---

class MainPage(webapp.RequestHandler):
	def get(self):
		citations = db.GqlQuery("SELECT * FROM Citation ORDER BY date_citation DESC LIMIT 50")

		for citation in citations:
			self.response.out.write("Le %s, %s nous rapportait une citation de %s : " %
									citation.date_record, citation.author, citation.author_original)
			self.response.out.write("<blockquote>%s</blockquote>" %
						         	cgi.escape(citation.content))
# ---

application = webapp.WSGIApplication(
									[('/', MainPage),
									('/ajout', MainPage)],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()