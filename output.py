#!/usr/bin/env python

import sys
if sys.version_info < (3, 0):
	PYTHON2 = True
	from output2 import *
else:
	PYTHON2 = False
	from output3 import *
