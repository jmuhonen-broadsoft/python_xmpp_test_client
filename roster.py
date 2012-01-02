#!/usr/bin/env python


import sleekxmpp
import threading
from base import *

class RosterHandler(XmppHandler):
	def __init__(self, xml):
		XmppHandler.__init__(self, xml)

		self.add_event_handler("session_start", self.start)
		self.action = None
		self.jids = set([])

	def setAction(self, action, jids):
		self.action = action
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

		print('Roster for %s' % self.boundjid.bare)
		for jid in self.client_roster:
			print(" " + jid)

		self.add_event_handler("roster_update", self.roster_update)

		disconnect = (jids == None or len(self.jids) == 0 or self.action not in ["add", "del"])
		if self.action == "add":
			print()
			for jid in self.jids:
				self.client_roster.add(jid)
				self.client_roster.subscribe(jid)
		elif self.action == "del":
			print()
			for jid in self.jids:
				self.client_roster.unsubscribe(jid)
				self.client_roster.remove(jid)
		elif self.action == "save":
			fname = list(self.jids)[0] if len(self.jids) == 1 else "roster.txt"
			with open(fname, "w") as r_file:
				print("saving to", fname)
				r_file.truncate()
				for jid in self.client_roster:
					r_file.write(jid + "\n")
		elif self.action != None:
			print("Unknown action: " + self.action)

		if disconnect:
			self.disconnect()

	def roster_update(self, event):
		event.enable("roster")
		items = event["roster"]["items"]
		jids = items.keys()
		if len(jids) == 1:
			jid = list(jids)[0]
			if jid in self.jids:
				if self.action == "del":
					print("Deleted", jid)
				elif self.action == "add":
					print("Added", jid)

				self.jids.remove(jid)

		if len(self.jids) == 0:
			print("Done, disconnecting")
			self.disconnect()


import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	filename = sys.argv[1] if len(sys.argv) > 1 else "config.xml"
	action = sys.argv[2] if len(sys.argv) > 2 else None

	jids = None
	if len(sys.argv) > 3:
		try:
			with open(sys.argv[3], "r") as file:
				jids = file.read().splitlines()
		except IOError as e:
			jids = []
			for i in range(3, len(sys.argv)):
				jids.append(sys.argv[i])

	with open(filename, "r") as config:
		client = RosterHandler( config.read() )
		client.setAction( action, jids )
		if client.connect():
			client.process(block=True)
