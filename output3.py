#!/usr/bin/env python

from threading import Lock

plock = Lock()
def output(what = ""):
	with plock:
		print(what)