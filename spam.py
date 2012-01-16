#!/usr/bin/env python

from msg import *

def usage():
	usage = "usage:\npython spam.py [config file with server details] [jid(s) + passwd(s) file] [recipient] [message | filename to a file from where the message is read]\n"
	usage += "examples:\n"
	usage += "python spam.py config.xml users.txt foo@bar.com \"Hello\"\n"
	usage += "python spam.py config.xml users.txt foo@bar.com msg.txt\n"
	return usage


import sys

if len(sys.argv) > 0 and __file__ == sys.argv[0]:
	if len(sys.argv) == 1:
		output(usage())

	if len(sys.argv) > 4:
		conf_file = sys.argv[1]
		jids_file = sys.argv[2]

		to = sys.argv[3]
		txt = sys.argv[4]
		try:
			file = open(txt, "r")
			txt = file.read()
		except:
			pass

#		splitters = ["\t", " "]
		with open(conf_file, "r") as conf:
			config = conf.read()
			with open(jids_file, "r") as file:
				msgs = 0
				for line in file:
					msgs += 1
					stuff = line.split(" ")
					usr = stuff[0].strip()
					pwd = stuff[1].strip()
					output("\n-------------------------------------------------")
					output( "logging in with: \"" + usr + "\" + \"" + pwd + "\"" )

					client = MsgHandler( config, username = usr, password = pwd )
					client.setMessage( to, str(msgs) + ": " + txt )
					if client.connect():
						client.process(block=True)
					output("-------------------------------------------------\n")