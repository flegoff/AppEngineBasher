import re
import cgi
import logging
import yaml

from datetime import datetime

import basherc

from google.appengine.api import xmpp
from google.appengine.ext import webapp
from google.appengine.ext import db
from google.appengine.ext.webapp.util import run_wsgi_app

# ---

class XMPPHandler(webapp.RequestHandler):
    
    def __init__(self):
        self.config = yaml.load(file('basher.yaml', 'r'))
        
    def send_invite(self, message):
        logging.info("[basher] message discarded (f=%s)" % message.sender)
        message.reply("Oops... please format your message this way : &author name&quote&")
        message.reply("For example:  &Douglas Adams&Don't Panic&")
        message.reply("Or, if you want to try to add a date on it, use this new format, with \
            the date encoded as YYYYMMMDD at the end.")
        message.reply(" -- 20081201 gives the first of december of 2008 --")
        message.reply("&Douglas Adams&Don't Panic&20080101")
    
    def post(self):
        message = xmpp.Message(self.request.POST)
        logging.info("[basher] message is /%s/" % message.body)

        quote = basherc.Quote()
        
        reg = re.compile('^\&([^\&]+)\&([^\&]+)\&(\d{8})?$')
        m = reg.match(message.body)
        
        if not m:
            return self.send_invite(message)
            
        quote.author = message.sender
        quote.author_original = m.group(1)
        quote.content = m.group(2)
        
        # we're trying to convert the date, here, dude
                    
        try:
            if m.group(3):
                quote.date_quote = datetime.strptime(m.group(3), '%Y%m%d')
            quote.put()

            logging.info("[basher] message stored")
            message.reply("Thank you ! You may want to check %s now." % self.request.host_url)

            # sends a Jabber msg to the admins

            if self.config['warn_xmpp']:
                try :
                    xmpp.send_message(self.config['warn_xmpp'], "A new quote was added : %s" % quote.content)
                except:
                    loggin.warning("[basher] unable to warn")
                
        except ValueError:
            message.reply("The date " + m.group(3) + " is invalid !")
                

# ---

application = webapp.WSGIApplication(
                                    [('/_ah/xmpp/message/chat/', XMPPHandler)],
                                    debug=True)

def main():
    run_wsgi_app(application)

if __name__ == "__main__":
    main()
