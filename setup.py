#!/usr/bin/env python

from __future__ import print_function
from os import popen, chdir
import sys

branch = "python2" if PYTHON2 else "python3"
executable = sys.executable
print("Using python from %s" % executable)
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
	print(popen(executable + " setup.py install").read())
	chdir("../dnspython")
	print(popen(executable + " setup.py install").read())
	chdir("..")
	print("Text client has been updated!")
