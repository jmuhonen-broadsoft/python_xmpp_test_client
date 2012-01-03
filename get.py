#!/usr/bin/env python

import urllib.request as request
from base import *

def getDm(dm_url, dm_usr, dm_pwd):
	if dm_usr is not None and dm_usr is not None:
		pwd_mgr = request.HTTPPasswordMgrWithDefaultRealm()
		pwd_mgr.add_password(None, dm_url, dm_usr, dm_pwd)
		handler = request.HTTPBasicAuthHandler(pwd_mgr)
		opener = request.build_opener(handler)
		request.install_opener(opener)

	req = request.urlopen(dm_url)
	return req.read()

def writeDm(dm_cfn, dm_xml):
	with open(dm_cfn, 'wb') as file:
		file.truncate()
		file.write(dm_xml)

def usage():
	usage = "usage:\npython get.py [device management url] [username] [password] (file name for downloaded content)\n"
	return usage


import sys

if len(sys.argv) == 1:
	output(usage())
elif len(sys.argv) > 1 and __file__ == sys.argv[0]:
	dm_url = sys.argv[1]
	dm_cfn = sys.argv[4] if len(sys.argv) > 4 else "config.xml"
	dm_usr = None
	dm_pwd = None
	if len(sys.argv) > 3:
		dm_usr = sys.argv[2]
		dm_pwd = sys.argv[3]

	try:
		xml = getDm(dm_url, dm_usr, dm_pwd)
	except:
		output("get failed")
		exit()

	writeDm(dm_cfn, xml)
