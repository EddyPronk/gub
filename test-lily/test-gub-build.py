#!/usr/bin/python
import sys
import os
import re
import time


def system (c, ignore_error=False):
	print 'executing' , c
	s = os.system (c)
	if s and not ignore_error:
		raise 'barf'

def test_build (bin):
	if bin.find (':') < 0:
		bin = os.path.abspath (bin)

	base = os.path.split (bin)[1]

	platform = ''
	for p in ('linux', 'freebsd', 'darwin-ppc', 'darwin-x86', 'mingw'):
		if re.search (p, base):
			platform = p
			break

	if not platform:
		print 'unknown platform for', bin
		return

	ending_found = 0 
	for e in ['.sh', '.zip', '.exe', 'tar.bz2']:
		ending_found = ending_found or base.endswith  (e)

	if not ending_found:
		print 'unknown extension for', base
		return
	
	
	
	try:
		os.unlink ('typography-demo.pdf')
	except:
		pass

	print 'testing platform %s' % platform

	test_file = 'downloads/lilypond-HEAD/input/typography-demo.ly'
	test_result =  '%s.test.pdf' % base

	if platform == 'linux':
		system ('cp %s /tmp/ ' % test_file)
		system ('sudo su - test -c "sh -x test-linux-gub.sh %s"' % bin)
		system ('cp ~test/test-gub/typography-demo.pdf %s' % test_result)
	elif platform == 'darwin-x86':
		system ('touch %s ' % test_result)
	elif platform == 'darwin-ppc':
		system ('scp %s maagd:test/' % bin)
		system ('slogin maagd sh -x test-macosx-gub.sh %s' % base)
		system ('scp %s maagd:test/' % test_file)
		system ('scp maagd:test/typography-demo.pdf %s' % test_result)
		system ('slogin maagd rm test/%s' % base)
	elif platform == 'mingw':
		system ('scp %s wklep:test/ ' % bin)
		system ('slogin wklep sh -x test-mingw-gub.sh %s ' % base)
		system ('scp wklep:test/typography-demo.pdf %s' % test_result)
	elif platform == 'freebsd':
		host = 'xs4all'
		system ('slogin %s test-gub/bin/uninstall-lilypond --quiet ' % host, ignore_error=True)
		system ('scp %s %s %s:test-gub/' % (bin, test_file, host))
		system ('slogin %s test-freebsd-gub.sh %s' % (host, base))
		system ('scp %s:test-gub/typography-demo.pdf %s' % (host,test_result))

	system ('mv %s log/' %  test_result)
	system ('xpdf log/%s &' % test_result)

pids = []
for a in sys.argv[1:]:
	pid = os.fork () 
	if not pid:
		test_build (a)
		sys.exit (0)
	else:
		pids.append (pid)

os.wait()
