#!/usr/bin/env python

from base import *
import time

class MsgHandler(XmppHandler):
	def __init__(self, xml, username = None, password = None):
		XmppHandler.__init__(self, xml, username, password)

		self.add_event_handler("session_start", self._start, threaded=False)
		self.msg = None

	def setMessage(self, to, txt):
		self.msg = {"to": to, "txt": txt}

	def _start(self, event):
		output("started")
		try:
			self.get_roster()
		except IqError as err:
			output("Error: %s" % err.iq['error']['condition'])
		except IqTimeout:
			output("Error: Request timed out")

		self.send_presence()
		self.send_message( mfrom=self.boundjid.bare, mto=self.msg["to"], mbody=self.msg["txt"], mtype="chat" )
		output("Message \"%s\" sent to %s" %(self.msg["txt"], self.msg["to"])) 
		time.sleep(1)
		self.disconnect()

def usage():
	usage = "usage:\npython msg.py [config file path] [recipient] [message | filename to a file from where the message is read]"
	usage += "examples:\n"
	usage += "python msg.py config.xml user@server.com \"Hello\"\n"
	usage += "python msg.py config.xml user@server.com msg.txt\n"
	return usage


import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	if len(sys.argv) == 1:
		output(usage())

	if len(sys.argv) > 3:
		filename = sys.argv[1]
		to = sys.argv[2]
		txt = sys.argv[3]
		try:
			file = open(txt, "r")
			txt = file.read()
		except:
			pass
		
		with open(filename, "r") as config:
			client = MsgHandler( config.read() )
			client.setMessage( to, txt )
			if client.connect():
				client.process(block=True)
