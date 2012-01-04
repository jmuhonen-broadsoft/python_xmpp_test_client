#!/usr/bin/env python

from os import popen, chdir
import sys
from output import *

branch = "python2" if PYTHON2 else "python3"
executable = sys.executable
output("Using python from %s" % executable)
if platform.system() in ["Linux", "Darwin"]:
	executable = "sudo " + executable

popen("git fetch").read()
popen("git checkout " + branch )
popen("git rebase origin/" + branch )
popen("git submodule init")
popen("git submodule sync")
submod = popen("git submodule update").read()
if len(submod) > 0:
	chdir("SleekXMPP")
	output(popen(executable + " setup.py install").read())
	chdir("../dnspython")
	output(popen(executable + " setup.py install").read())
	chdir("..")
	output("Text client has been updated!")
