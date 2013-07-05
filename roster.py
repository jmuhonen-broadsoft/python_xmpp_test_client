#!/usr/bin/env python

from __future__ import print_function
import sleekxmpp
from base import *

class RosterHandler(XmppHandler):
	def __init__(self, xml, username = None, password = None):
		XmppHandler.__init__(self, xml, username, password)

		self.add_event_handler("session_start", self._start, threaded=True)
		self.action = None
		self.jids = set()

	def setAction(self, action, jids):
		self.action = action if action != "subs" else "add"
		if jids != None:
			self.jids = set(jids)

	def _start(self, event):
		print("started")
		try:
			self.get_roster()
		except IqError as err:
			print('Error: %' % err.iq['error']['condition'])
		except IqTimeout:
			print('Error: Request timed out')

		if self.action == "pres":
			self.send_presence()
			print('Waiting for presence updates...\n')
			self.await_for = set([self.boundjid.bare]) | set(self.client_roster)
			self._wait_for_presence()

		text = "Roster for %s" % ( self.boundjid.bare )
		if self.action == "pres":
			pres = self.presence_to_str( self.boundjid.bare )
			if pres is not None:
				text += " " + pres
		print( text )

		print("-" * 60)
		names = []
		max_nl = 0
		jids = []
		max_jl = 0
		details = []
		for jid in sorted( self.client_roster ):
			if jid is not self.boundjid.bare:
				item = self.client_roster[jid]
				names.append( item["name"] )
				max_nl = max( max_nl, len( item["name"] ))
				jids.append( jid )
				max_jl = max( max_jl, len( jid ))
				text = "[ ss: %-*s pending: %-*s waiting: %-*s]" % ( 5, item["subscription"] + ",", 6, str(item["pending_in"]) + ",", 6, item["pending_out"])
				if self.action == "pres":
					pres = self.presence_to_str( jid )
					text += " (" + ( pres if pres is not None else "No presence information" ) +")"
				details.append( text )
		
		for name, jid, detail in zip( names, jids, details ):
			print( name + " " * (max_nl - len( name ) + 1) + "\t" + jid +  " " * (max_jl - len( jid ) + 1) + "\t" + detail )
		print()

		if self.action == "gen":
			self.action = list(self.jids)[0] if len(self.jids) > 0 else "add"
			jids = []
			if self.action == "add":
				how_many = int(list(self.jids)[1]) if len(self.jids) > 1 else 1
				id = "gen." + gen_chars(8) + ".%d@generated.com"
				print("generating %d contacts" % how_many)
				for i in range(how_many):
					jids.append(id % i)
			elif self.action == "del":
				print("Deleting generated contacts")
				for jid in self.client_roster:
					if jid.startswith("gen.") and jid.endswith("@generated.com"):
						jids.append(jid)
			self.jids = set(jids)

		if self.boundjid.bare in self.jids:
			self.jids.remove( self.boundjid.bare )
		jids = self.jids.copy()
		self.add_event_handler("roster_update", self._roster_update)
		disconnect = (jids == None or len(jids) == 0 or self.action not in ["add", "addonly", "del", "unsubs"])
		if self.action in ["add", "addonly"]:
			not_handled = 0
			for jid in jids:
				item = self.client_roster[jid]
				if item is None or (item["subscription"] is "none" and not item["pending_out"] or item["subscription"] is "from" and item["pending_in"]):
					print( "adding %s" % jid )
					self.client_roster.add(jid)
					self.client_roster.subscribe(jid)
					if self.action == "addonly":
						self.client_roster.unsubscribe(jid)
				else:
					not_handled += 1
					print( "%s already subscribed (%d/%d)" % ( jid, not_handled, len(jids) ))
					disconnect = (len(jids) == not_handled)
		elif self.action == "del":
			for jid in jids:
				self.client_roster.unsubscribe(jid)
				self.client_roster.remove(jid)
		elif self.action == "unsubs":
			print()
			not_handled = 0
			for jid in jids:
				if self.client_roster[jid]["subscription"] in ["to", "both"]:
					self.client_roster.unsubscribe(jid)
				else:
					not_handled += 1
					print( "%s not subscribed" % ( jid ))
					disconnect = (len(jids) == not_handled)
		elif self.action == "save":
			fname = list(jids)[0] if len(jids) == 1 else "roster.txt"
			with open(fname, "w") as r_file:
				print("saving to %s" % fname)
				r_file.truncate()
				for jid in self.client_roster:
					if jid is not self.boundjid.bare:
						r_file.write(jid + "\n")
		elif self.action not in [None, "pres", "gen"]:
			print("Unknown action: %s" % (self.action))

		if disconnect:
			self.disconnect()

	def _roster_update(self, event):
		event.enable("roster")
		items = event["roster"]["items"]
		jids = items.keys()
		for jid in jids:
			if jid in self.jids:
				if self.action == "del":
					print("Deleted and unsubscribed %s" % (jid))
				elif self.action == "unsubs":
					print("Unsubscribed %s" % (jid))
				elif self.action.startswith( "add" ):
					added = "Added" + (" and subscribed" if len(self.action) == 3 else "") + " %s"
					print(added % (jid))

				self.jids.remove(jid)

		if len(self.jids) == 0:
			print("Done, disconnecting")
			self.disconnect()

def usage():
	usage = "usage:\npython roster.py\n"
	usage += "\t[config file path] & (userame:password)\n"
	usage += "\t\t[ add | addonly | del | gen | pres | save | subs | unsubs]\n"
	usage += "\t\t\t[file with jids separated by line end | list of jids | [add [amount] | del] | file to save your roster to]\n"
	usage += "examples:\n"
	usage += "python roster.py config.xml <command> roster.txt (command: add/addonly/del/subs/unsubs)\n"
	usage += "python roster.py config.xml <command> dude@server.com dude2@place.net (command: add/addonly/del/subs/unsubs)\n"
	usage += "python roster.py config.xml pres\n"
	usage += "python roster.py config.xml gen add 12\n"
	usage += "python roster.py config.xml gen del\n"
	usage += "python roster.py config.xml save roster.txt\n"
	usage += "python roster.py config.xml user:pwd save roster.txt\n"
	return usage


import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	if len(sys.argv) == 1:
		print(usage())

	filename = sys.argv[1] if len(sys.argv) > 1 else "config.xml"
	action = sys.argv[2] if len(sys.argv) > 2 else None
	if action is not None and ":" in action:
		data = action.split(":")
		username = data[0]
		password = data[1]
		action = sys.argv[3] if len(sys.argv) > 3 else None
		argv = 4
	else:
		username = None
		password = None
		argv = 3

	jids = None
	if len(sys.argv) > argv:
		try:
			with open(sys.argv[argv], "r") as file:
				jids = file.read().splitlines()
		except IOError as e:
			jids = []
			for i in range(argv, len(sys.argv)):
				jids.append(sys.argv[i])

	try:
		with open(filename, "r") as config:
			client = RosterHandler( config.read(), username, password )
			client.setAction( action, jids )
			if client.connect():
				client.process(block=True)
	except IOError as e:
		print( "config file %s could not be opened" % filename )