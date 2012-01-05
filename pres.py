#!/usr/bin/env python

from base import *

class Presence:
	show_values = list(sleekxmpp.stanza.Presence.types)[:2] + list(sleekxmpp.stanza.Presence.showtypes)

	def __init__(self, show, text, prio):
		self.show = show
		self.text = text
		self.prio = prio

class PresHandler(XmppHandler):
	def __init__(self, xml):
		XmppHandler.__init__(self, xml)

		self.add_event_handler("session_start", self._start, threaded=True)
		self.presence = None

	def setPresence(self, presence):
		self.presence = presence

	def _start(self, event):
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
		self.await_for = set([self.boundjid.bare])
		self._wait_for_presence()

		pres = self.presence
		if pres is not None:
			self.add_event_handler("changed_status", self._changed_status, threaded=True)
			self.send_presence( pshow = pres.show, pstatus = pres.text, ppriority = pres.prio )
		else:
			output("no presence set, disconnecting")
			self.disconnect()

	def _changed_status(self, pres):
		if pres is not None and pres['from'].bare == pres['to'].bare:
			show = (pres['show'] == self.presence.show or (pres['show'] == "" and self.presence.show == "available"))
			status = (pres['status'] == ("" if self.presence.text == None else self.presence.text))
			prio = (str(pres['priority']) == ("0" if self.presence.prio == None else self.presence.prio))
#			output(show, status, prio)
			if show and status and prio:
				self.del_event_handler("changed_status", self._changed_status)
				output("Own presence updated")
#				output(pres)
				text = "Press any key to disconnect"
				if PYTHON2:
					raw_input(text)
				else:
					input(text)
				self.disconnect()

def usage():
	usage = "usage:\npython pres.py [config file path] (content for show) (content for free text) (priority)\n"
	usage += "values for show: " + str(Presence.show_values) + "\n"
	usage += "after publish has been done, you can keep the client online as long as you want"
	usage += "examples:\n"
	usage += "python pres.py config.xml dnd\n"
	usage += "python pres.py config.xml dnd \"this is my free text\"\n"
	usage += "python pres.py config.xml dnd \"this is my free text\" 120\n"
	return usage


import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	if len(sys.argv) == 1:
		output(usage())

	filename = sys.argv[1] if len(sys.argv) > 1 else "config.xml"

	presence = None
	if len(sys.argv) > 2:
		show = sys.argv[2]
		force = sys.argv[5].lower() == "true" if len(sys.argv) > 5 else False
		if show not in Presence.show_values and not force:
			output("Unable to publish show values outside of " + str(Presence.show_values))
			output("Call: python pres.py " + show + " freetext priority true - to try publishing. This is not supported operation!")
			exit()
		
		text = sys.argv[3] if len(sys.argv) > 3 and len(sys.argv[3]) > 0 else None
		prio = sys.argv[4] if len(sys.argv) > 4 else None
#		output( sys.argv[2:] )
		presence = Presence( show, text, prio )

	with open(filename, "r") as config:
		client = PresHandler( config.read() )
		client.setPresence( presence )
		if client.connect():
			client.process(block=True)
