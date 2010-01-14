import re
import cgi
import logging
import yaml

import basherc

from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

# ---

class XMPPHandler(webapp.RequestHandler):
	
	def __init__(self):
		self.config = yaml.load(file('basher.yaml', 'r'))
	
	def post(self):
		message = xmpp.Message(self.request.POST)
		logging.info("[basher] message is /%s/" % message.body)

		quote = basherc.Quote()
		
		reg = re.compile('^\&([^\&]+)\&([^\&]+)\&')
		m = reg.match(message.body)
		
		try :
			quote.author = message.sender
			quote.author_original = m.group(1)
			quote.content = m.group(2)
			quote.put()
			logging.info("[basher] message stored")
			message.reply("Thank you ! You may want to check %s now." % self.request.host_url)
			
			# sends a Jabber msg to the admins
			if self.config['warn_xmpp']:
				try :
					logging.info("[basher] warning the admins : %s" % self.config['warn_xmpp'])
					xmpp.send_message(self.config['warn_xmpp'], "A new quote was added : %s" % quote.content)
				except:
					loggin.warning("[basher] unable to warn")
			
		except:
			logging.info("[basher] message discarded (f=%s)" % message.sender)
			message.reply("Oops... please format your message this way : &author name&quote& . For example : &Douglas Adams&Don't Panic&")

# ---

application = webapp.WSGIApplication(
									[('/_ah/xmpp/message/chat/', XMPPHandler)],
									debug=True)

def main():
	run_wsgi_app(application)

if __name__ == "__main__":
	main()
