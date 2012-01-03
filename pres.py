#!/usr/bin/env python

from base import *

class Presence:
	def __init__(self, show, text, prio):
		self.show = show
		self.text = text
		self.prio = prio

class PresHandler(XmppHandler):
	def __init__(self, xml):
		XmppHandler.__init__(self, xml)

		self.add_event_handler("session_start", self.start)
		self.presence = None

	def setPresence(self, presence):
		self.presence = presence

	def start(self, event):
		output("started")
		try:
			self.get_roster()
		except IqError as err:
			output("Error: %s" % err.iq['error']['condition'])
		except IqTimeout:
			output("Error: Request timed out")

		self.send_presence()
		if not self.sentpresence:
			output("Didn't send presence...")
		output("Waiting for presence updates...\n")
		self.await_for = set(self.boundjid.bare)
		self.wait_for_presence(5)

		self.add_event_handler("changed_status", self.changed_status)
		pres = self.presence
		if pres is not None:
			self.send_presence( pshow = pres.show, pstatus = pres.text, ppriority = pres.prio )
		else:
			output("no presence set, disconnecting")
			self.disconnect()

	def changed_status(self, pres):
		if pres['from'].bare == pres['to'].bare:
			show = (pres['show'] == self.presence.show or (pres['show'] == "" and self.presence.show == "available"))
			status = (pres['status'] == ("" if self.presence.text == None else self.presence.text))
			prio = (str(pres['priority']) == ("0" if self.presence.prio == None else self.presence.prio))
#			output(show, status, prio)
			if show and status and prio:
				self.del_event_handler("changed_status", self.changed_status)
				output("Own presence updated")
#				output(pres)
				input("Press any key to disconnect")
				self.disconnect()

import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	filename = sys.argv[1] if len(sys.argv) > 1 else "config.xml"

	presence = None
	if len(sys.argv) > 2:
		show = sys.argv[2]
		text = sys.argv[3] if len(sys.argv) > 3 and len(sys.argv[3]) > 0 else None
		prio = sys.argv[4] if len(sys.argv) > 4 else None
		presence = Presence( show, text, prio )

	with open(filename, "r") as config:
		client = PresHandler( config.read() )
		client.setPresence( presence )
		if client.connect():
			client.process(block=True)