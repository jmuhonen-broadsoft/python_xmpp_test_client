#!/usr/bin/env python

from base import *

class PresHandler(XmppHandler):
	def __init__(self, xml):
		XmppHandler.__init__(self, xml)

		self.add_event_handler("session_start", self.start)
		self.presence = None

	def setPresence(self, presence):
		self.presence = presence
		if jids != None:
			self.jids = set(jids)

	def start(self, event):
		print("started")
		try:
			self.get_roster()
		except IqError as err:
			print('Error: %' % err.iq['error']['condition'])
		except IqTimeout:
			print('Error: Request timed out')

		print('Waiting for presence updates...\n')
		self.await_for = set(self.boundjid.bare)
		self.wait_for_presence(5)

		print(self.boundjid.bare)
#		print_pres(self.boundjid.bare)

		self.disconnect()

import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	filename = sys.argv[1] if len(sys.argv) > 1 else "config.xml"

	with open(filename, "r") as config:
		client = PresHandler( config.read() )
		if client.connect():
			client.process(block=True)