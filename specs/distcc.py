#!/usr/bin/env python
import sys
import os
import re
import telnetlib
import socket

port = 3633

def live_hosts (hosts):
	live = []
	for h in hosts:
		try:
			t = telnetlib.Telnet(h, port)
			t.close ()
		except socket.error:
			continue

		live.append ('%s:%d' % (h,port))

	if live:
		'DISTCC live hosts: ', live
	return live



def main ():
	exe_name = os.path.split (sys.argv[0])[1]
	path_comps = [c for c in os.environ['PATH'].split (':') if not re.search ('distcc', c)]
	os.environ['PATH'] = ':'.join (path_comps)
	argv = ['distcc', exe_name] + sys.argv[1:]
##	sys.stderr.write ('execing: %s' % ' '.join (argv))
	os.execvp ('distcc', argv)

if __name__ == '__main__':
	main()
