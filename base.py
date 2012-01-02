#!/usr/bin/env python

import xml.etree.ElementTree as ET
import random, string
import sleekxmpp
import threading

class XmppDetails:
	def __init__(self, server, port, secure, username, password, resource):
		chars = string.ascii_lowercase + string.digits
		username = username + "/" + resource + "_broadsoft_text_client_" + "".join([random.choice(chars) for i in range(8)])

		self.server = server
		self.port = port if port != None and len(port) > 0 else 5222
		self.secure = secure
		self.username = username
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
	server = service.text
	port = service.get("port")

	secure = xmpp.find("ssl").get("enabled") == "true"
	resource = xmpp.find("resource").text

	return XmppDetails(server, port, secure, username, password, resource)


class XmppHandler(sleekxmpp.ClientXMPP):
	def __init__(self, xml):
		details = extractXmppDetails(xml)
		sleekxmpp.ClientXMPP.__init__(self, details.username, details.password)
		self.details = details

		self.add_event_handler("changed_status", self.changed_status)
		self.await_for = None
		self.received = set()
		self.presences_received = threading.Event()

	def connect(self):
		conn = None
		if not sleekxmpp.clientxmpp.DNSPYTHON:
			conn = (self.details.server, self.details.port)

		return sleekxmpp.ClientXMPP.connect( self, conn, False, self.details.secure )

	def wait_for_presence(self, how_many):
		if self.await_for is not None:
			self.await_for = self.await_for - self.received
			if len(self.await_for) > 0:
				self.presences_received.wait(how_many)

	def changed_status(self, pres):
		from_jid = pres["from"].bare
		if self.await_for is None:
			self.received = from_jid
			return

		if from_jid in self.await_for:
			self.await_for.remove(jid)

		if len(self.await_for) != 0:
			self.presences_received.clear()
		else:
			self.presences_received.set()

	def print_pres(connections):
		if connections is not None:
			print(connections)
			for res, pres in connections.items():
				show = pres["show"] if pres["show"] else "??????"
				status = pres["status"] if pres["status"] else "??????"
				print( " + res: {0} show: {1} status: {2}".format( res, show, status ))

