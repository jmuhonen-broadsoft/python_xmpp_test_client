#!/usr/bin/env python

from os import popen, chdir
import sys
from base import *

branch = "python2" if sys.version_info < (3, 0) else "python3"
executable = sys.executable
output("Using python from %s" % executable)

fetching = popen("git fetch").read()
if len(fetching) > 0:
	popen("git checkout " + branch )
	popen("git rebase origin/" + branch )
	popen("git submodule init")
	popen("git submodule sync")
	submod = popen("git submodule update").read()
	if len(fetching) > 0:
		chdir("SleekXmpp")
		output(popen(executable + "setup.py install").read())
		chdir("../dnspython")
		output(popen(executable + "setup.py install").read())
		chdir("..")
		output("Text client has been updated!")
