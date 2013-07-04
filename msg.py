#!/usr/bin/env python

from __future__ import print_function
from base import *
import time

class MsgHandler(XmppHandler):
	def __init__(self, xml, username = None, password = None):
		XmppHandler.__init__(self, xml, username, password)

		self.add_event_handler("session_start", self._start, threaded=False)
		self.msg = []
		self.sleep = 1

	def add_message(self, to, txt):
		self.msg.append({"to": to, "txt": txt})

	def set_sleep(self, sleep):
		self.sleep = sleep

	def _start(self, event):
		print("started")
		try:
			self.get_roster()
		except IqError as err:
			print("Error: %s" % err.iq['error']['condition'])
		except IqTimeout:
			print("Error: Request timed out")

		self.send_presence()
		for msg in self.msg:
			self.send_message( mfrom=self.boundjid, mto=msg["to"], mbody=msg["txt"], mtype="chat" )
			print("Message \"%s\" sent to %s" %(msg["txt"], msg["to"])) 
			time.sleep(self.sleep)
		self.disconnect()

def usage():
	usage = "usage:\npython msg.py [config file path] [recipient] [message | filename to a file from where the message is read] (amount)"
	usage += "examples:\n"
	usage += "python msg.py config.xml user@server.com \"Hello\"\n"
	usage += "python msg.py config.xml user@server.com msg.txt 7\n"
	return usage


import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	if len(sys.argv) == 1:
		print(usage())

	if len(sys.argv) > 3:
		filename = sys.argv[1]
		to = sys.argv[2]
		txt = sys.argv[3]
		amount = int(sys.argv[4]) if len(sys.argv) > 4 else 1
		try:
			file = open(txt, "r")
			txt = file.read()
		except:
			pass
		
		with open(filename, "r") as config:
			client = MsgHandler( config.read() )
			if amount > 1:
				for i in range(1, amount + 1):
					client.add_message( to, txt + " (" + i + ")" )
			else:
				client.add_message( to, txt )

			if client.connect():
				client.process(block=True)
