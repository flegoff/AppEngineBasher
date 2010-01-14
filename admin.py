import os
import re
import cgi
import logging

import basherc

from google.appengine.api import users
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

# ---

class AdminPage(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()		

		if user and users.is_current_user_admin():
			quotes = db.GqlQuery("SELECT * FROM Quote ORDER BY date_quote DESC LIMIT 50")
			mt = basherc.MiniTemplateRenderer(self.response)
			mt.produce_index({ 'quotes': quotes, 'adminmode': True, 'user': "<a href='" + users.create_logout_url('/') + "'>" + user.nickname() + "</a>" })

		else:
			self.redirect(users.create_login_url(self.request.uri))

# ---

class AdminAction(webapp.RequestHandler):
	def get(self):
		user = users.get_current_user()		

		if user and users.is_current_user_admin():
			quote = db.get(self.request.get('id'))
			logging.info("[admin] located quote by %s" % quote.author)
			quote.delete()
			logging.warning("[admin] quote was deleted by %s" % user.nickname())
			self.redirect("/admin/")
			
		else:
			self.redirect("/admin/")

# ---

application = webapp.WSGIApplication(
									[('/admin/delete', AdminAction),
									('/admin/', AdminPage)],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()