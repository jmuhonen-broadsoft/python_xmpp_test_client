#!/usr/bin/env python

import xml.etree.ElementTree as ET
import random, string
import sleekxmpp

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

	def connect(self):
		conn = None
		if not sleekxmpp.clientxmpp.DNSPYTHON:
			conn = (self.details.server, self.details.port)

		return sleekxmpp.ClientXMPP.connect( self, conn, False, self.details.secure )