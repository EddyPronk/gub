#!/usr/bin/python

## interaction with lp.org down/upload area.

import os
import urllib
import re
import string
import sys

platforms = ['linux-x86',
	     'darwin-ppc',
	     'freebsd-x86',
#	     'linux-arm',
	     'mingw']

def get_alias (p):
	try:
		return {
			'linux-x86': 'linux',
			'darwin-ppc': 'darwin',
			'linux-arm': 'arm',
			'freebsd-x86': 'freebsd',
			}[p]
	except KeyError:
		return p

formats = {
	'linux-x86': 'sh',
	'darwin-ppc': 'zip',
	'freebsd-x86': 'sh',
	'mingw':'exe',
	'linux-arm': 'sh',
	}

def system (c):
	print c
	if os.system (c):
		raise 'barf'

def get_url_versions (url):
	index = urllib.urlopen (url).read()

	versions = []
	def note_version (m):
		version = tuple (map (string.atoi,  m.group (1).split('.')))
		build = 0
		if m.group(2):
			build = string.atoi (m.group (2))
		
		versions.append ((version, build))
		return ''

	re.sub (r'lilypond-([0-9.]+)-?([0-9]+)?\.[a-z-]+\.[a-z-]+', note_version, index)
	return versions
	

def get_versions (platform):
	return get_url_versions ('http://lilypond.org/download/binaries/%(platform)s/'
			  % locals ())

def get_src_versions (maj_min_version):
	return get_url_versions ('http://lilypond.org/download/v%d.%d/' %
				 maj_min_version)

def get_max_builds (platform):
	vs = get_versions (platform)

	builds = {}
	for (version, build) in vs:
		if builds.has_key (version):
			build = max (build, builds[version])

		builds[version] = build

	return builds
	
def max_version_build (platform):
	vbs = get_versions (platform)
	vs = [v for (v,b) in vbs]
	vs.sort()
	max_version = vs[-1]

	max_b = 0
	for (v,b) in get_versions (platform):
		if v == max_version:
			max_b = max (b, max_b)

	return (max_version, max_b)

def max_src_version (maj_min):
	vs = get_src_versions (maj_min)
	vs.sort()
	return vs[-1][0]

def uploaded_build_number (version):
	platform_versions = {}
	build = 0
	for p in platforms:
		vs = get_max_builds (p)
		if vs.has_key (version):
			build = max (build, vs[version])

	return build

def upload_binaries (version):
	build = uploaded_build_number (version) + 1

	src_dests= []
	barf = 0
	for platform in platforms:
		plat = get_alias (platform)
		format = formats[platform]
		host = 'lilypond.org'
		version_str = '.'.join (['%d' % v for v in version])
		
		host_dir  = '/var/www/lilypond/download/binaries'
		base = 'lilypond-%(version_str)s-%(build)d.%(plat)s.%(format)s' % locals()
		bin = 'uploads/%(base)s' % locals()
		
		if not os.path.exists (bin):
			print 'binary does not exist', bin
			barf = 1
		elif not os.path.exists ('log/%s.test.pdf' % base):
			print 'test result does not exist for %s' % base
			barf = 1
			
		src_dests.append((bin, '%(host)s:%(host_dir)s/%(platform)s' % locals()))

	if barf:
		raise 'barf'
		
	for tup in src_dests:
		system ('scp %s %s' % tup)


if __name__ == '__main__':
	if len (sys.argv) <= 2:
		print '''use: lilypondorg.py


		nextbuild X.Y.Z
		upload x.y.z 

		'''
		
		sys.exit (1)

	if sys.argv[1] == 'nextbuild':
		version = tuple (map (string.atoi, sys.argv[2].split ('.')))
		print uploaded_build_number (version) + 1
	elif sys.argv[1] == 'upload':
		version = tuple (map (string.atoi, sys.argv[2].split ('.')))
		upload_binaries (version)
	else:
		print max_src_version ((2,7))
	#print max_version_build ('darwin-ppc')
	
	
	     
