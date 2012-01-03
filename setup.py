#!/usr/bin/env python

from os import popen, chdir
import sys
from base import *

branch = "python2" if sys.version_info < (3, 0) else "python3"

popen("git fetch")
popen("git checkout " + branch )
popen("git rebase origin/" + branch )
popen("git submodule init")
popen("git submodule sync")
popen("git submodule update")
chdir("SleekXmpp")
output(popen(sys.executable + "setup.py install").read())
chdir("../dnspython")
output(popen(sys.executable + "setup.py install").read())
chdir("..")
output("Text client has been updated!")
