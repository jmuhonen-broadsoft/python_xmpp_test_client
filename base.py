#!/usr/bin/env python

from __future__ import print_function
import xml.etree.ElementTree as ET
import random, string
import sleekxmpp
import threading


import logging
logging.basicConfig()

def gen_chars(amount):
	chars = string.ascii_lowercase + string.digits
	return "".join([random.choice(chars) for i in range(amount)])

class XmppDetails:
	def __init__(self, server, port, secure, username, password, resource):
		username = username if username is not None else "" + "/" + resource + "_broadsoft_text_client_" + gen_chars(8)

		self.server = server
		self.port = port if port != None and len(port) > 0 else 5222
		self.secure = secure if secure != None else False
		self.username = username
		self.password = password

	def set_username(self, username):
		splitted = self.username.split("/")
		self.username = username
		if splitted is not None and len(splitted) > 1:
			self.username += "/" + splitted[1]

	def set_password(self, password):
		self.password = password

def extractXmppDetails(xml):
	config = ET.fromstring(xml)
	if config is None or config.tag != "config":
		return None

	#use config version attribute to differentiate between versions
	xmpp = config.find("protocols").find("xmpp")
	if xmpp is None:
		return None

	creds = xmpp.find("credentials")
	username = creds.find("username").text
	password = creds.find("password").text

	service = xmpp.find("service-location")
	if service is not None:
		server = service.text
		port = service.get("port")
	else:
		server = None
		port = None

	secure = None
	ssl = xmpp.find("ssl")
	if ssl is not None:
		secure = ssl.get("enabled") == "true"
	else:
		ssl = xmpp.find("use-ssl")
		if ssl is not None:
			secure = ssl.text
	res = xmpp.find("resource")
	resource = res.text if res is not None else ""

	return XmppDetails(server, port, secure, username, password, resource)


class XmppHandler(sleekxmpp.ClientXMPP):

	def __init__(self, xml, username = None, password = None):
		details = extractXmppDetails(xml)
		if username is not None:
			details.set_username( username )
		if password is not None:
			details.set_password( password )

		sleekxmpp.ClientXMPP.__init__(self, details.username, details.password)
		self.details = details

		self.add_event_handler( "changed_status", self._changed_status )
		self.await_for = None
		self.received = set()
		self.presences = dict()

		self.presences_received = threading.Event()
		self.auto_authorize = False
		self.auto_subscribe = False

		if sleekxmpp.clientxmpp.DNSPYTHON:
			import dns.resolver
			dns.resolver.get_default_resolver().nameservers.extend(["8.8.8.8","8.8.4.4"])
			
	def get_details(self):
		return self.details

	def connect(self):
		conn = None
		if not sleekxmpp.clientxmpp.DNSPYTHON:
			conn = (self.details.server, self.details.port)

		return sleekxmpp.ClientXMPP.connect( self, conn, False, self.details.secure )

	def _wait_for_presence(self):
		if self.await_for is not None:
			self.await_for = self.await_for - self.received
			if len( self.await_for ) > 0:
				self.presences_received.wait( min( len( self.await_for ), 15 ))

	def _changed_status(self, pres):
		jid = pres["from"].bare
		self.presences[jid] = pres

		if self.await_for is None:
			self.received.add( jid )
			return

		if jid in self.await_for:
			self.await_for.remove( jid )

		if len(self.await_for) != 0:
			self.presences_received.clear()
		else:
			self.presences_received.set()

	def presence_to_str(self, jid):
		if jid in self.presences:
			pres = self.presences[jid]
			show = pres["show"] if pres["show"] != "" else "available"
			status = (" \"" + pres["status"] + "\"") if pres["status"] else ""
			return "%s%s" % ( show, status )
		return None
