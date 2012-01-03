#!/usr/bin/env python


import sleekxmpp
from base import *

class RosterHandler(XmppHandler):
	def __init__(self, xml):
		XmppHandler.__init__(self, xml)

		self.add_event_handler("session_start", self.start)
		self.action = None
		self.jids = set()

	def setAction(self, action, jids):
		self.action = action if action != "subs" else "add"
		if jids != None:
			self.jids = set(jids)

	def start(self, event):
		output("started")
		try:
			self.get_roster()
		except IqError as err:
			output('Error: %' % err.iq['error']['condition'])
		except IqTimeout:
			output('Error: Request timed out')

		if self.action == "pres":
			self.send_presence()
			output('Waiting for presence updates...\n')
			self.await_for = set(self.boundjid.bare) | set(self.client_roster) | set("foo@bar.com")
			self.wait_for_presence(15) #what number is this?!?

		output("Roster for %s" % ( self.boundjid.bare ))
		if self.action == "pres":
			XmppHandler.output_pres( None )

		output("-" * 60)
		for jid in self.client_roster:
			item = self.client_roster[jid]
			output("%s [ss: %s, pending: %s, waiting: %s]" % ( jid, item["subscription"], item["pending_in"], item["pending_out"]))
			if self.action == "pres":
				XmppHandler.output_pres( self.client_roster.presence( jid ))
		output()

		self.add_event_handler("roster_update", self.roster_update)

		disconnect = (jids == None or len(self.jids) == 0 or self.action not in ["add", "addonly", "del", "unsubs"])
		if self.action in ["add", "addonly"]:
			not_handled = 0
			for jid in self.jids:
				if self.client_roster[jid]["subscription"] not in ["to", "both"]:
					self.client_roster.add(jid)
					self.client_roster.subscribe(jid)
					if self.action == "addonly":
						self.client_roster.unsubscribe(jid)
				else:
					not_handled += 1
					output( "%s already subscribed" % ( jid ))
					disconnect = (len(self.jids) == not_handled)
		elif self.action == "del":
			for jid in self.jids:
				self.client_roster.unsubscribe(jid)
				self.client_roster.remove(jid)
		elif self.action == "unsubs":
			output()
			not_handled = 0
			for jid in self.jids:
				if self.client_roster[jid]["subscription"] in ["to", "both"]:
					self.client_roster.unsubscribe(jid)
				else:
					not_handled += 1
					output( "%s not subscribed" % ( jid ))
					disconnect = (len(self.jids) == not_handled)
		elif self.action == "save":
			fname = list(self.jids)[0] if len(self.jids) == 1 else "roster.txt"
			with open(fname, "w") as r_file:
				output("saving to %s" % fname)
				r_file.truncate()
				for jid in self.client_roster:
					r_file.write(jid + "\n")
		elif self.action not in [None, "pres"]:
			output("Unknown action: %s" % (self.action))

		if disconnect:
			if jids != None and len(self.jids) > 0:
				output("Nothing to be done")
			self.disconnect()

	def roster_update(self, event):
		event.enable("roster")
		items = event["roster"]["items"]
		jids = items.keys()
		if len(jids) == 1:
			jid = list(jids)[0]
			if jid in self.jids:
				if self.action == "del":
					output("Deleted and unsubscribed %s" % (jid))
				elif self.action == "unsubs":
					output("Unsubscribed %s" % (jid))
				elif self.action.startswith( "add" ):
					added = "Added" + (" and subscribed" if len(self.action) == 3 else "") + "%s"
					output(added % (jid))

				self.jids.remove(jid)

		if len(self.jids) == 0:
			output("Done, disconnecting")
			self.disconnect()

def usage():
	return "usage: python roster.py [config file path] [add | addonly | del | pres | save | subs | unsubs] [file with jids separated by line end | list of jids | file to save your roster to]"

import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	if len(sys.argv) == 1:
		output(usage())

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
