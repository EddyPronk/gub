#!/usr/bin/python
import os
import re
import sys
import string

host = 'hanwen@ssh.webdev.nl'
home = os.environ['HOME']
unpack_dir = home + '/nobackup/lilypond-local-web/doc'
MAJOR_VERSION=None
branch = 'HEAD'

py_platform_mapping = {
	'darwin': 'darwin-ppc',
	'linux2': 'linux',
}
platform = py_platform_mapping[sys.platform]

def do_urchin (filename):
	s = open (filename).read()
	if re.search ('UA-68969', s):
		return
	
	print 'instrumenting ', filename
	urchin_track = """<script src="http://www.google-analytics.com/urchin.js" type="text/javascript">
	</script>
	<script type="text/javascript">
_uacct = "UA-68969-1";
urchinTracker();
</script>"""
	
	s = re.sub ("(?i)</head>", urchin_track + '\n</head>', s)
	open (filename, 'w').write (s)

def system (cmd):
	print cmd
	stat = os.system (cmd)
	if stat:
		raise 'fail'
def read_version (vf):
	print 'reading', vf 
	for l in open (vf).readlines():
		def f(m):
			globals()[m.group(1)] = string.atoi (m.group(2))
			return ''

		l = re.sub ('^(MAJOR_VERSION|MINOR_VERSION|PATCH_LEVEL) *= *(.*)', f, l)

if sys.argv[1:]:
	branch = sys.argv[1]
	
cwd = os.getcwd ()
for dir in [cwd, cwd + '/downloads/lilypond-%s/' % branch]:
	if os.path.exists (dir + '/VERSION'):
		read_version (dir + '/VERSION')
		break
	
if not MAJOR_VERSION:
	raise 'not in lilydir'

webroot = None
for dir in [cwd, cwd +'/target/%s/build/lilypond-%s/' % (platform, branch)]:
	if os.path.exists (dir + '/out-www/web-root/'):
		webroot = dir +  '/out-www/web-root/'
		break
	

print 'dir=', unpack_dir
os.chdir (unpack_dir)
dir = 'v%s.%s' % (MAJOR_VERSION, MINOR_VERSION)
system ('rm -rf %s' % dir)
system ('mkdir  -p %s' % dir)
os.chdir (unpack_dir + '/' + dir)
system ('rsync -a %s/ . ' % webroot) # --link
system ('chmod -R g+w . ' )
system ('chgrp -R lilypond . ' )
system ('chmod 2755 `find -type d ` . ')

for f in ['Documentation/index.html',
	  'Documentation/topdocs/NEWS.html',
	  'Documentation/user/lilypond/index.html',
	  'Documentation/user/lilypond-internals/index.html',
	  'examples.html',
	  'Documentation/user/music-glossary/index.html',
	  'Documentation/topdocs/NEWS.html',
	  'Documentation/user/lilypond/Tutorial.html',
	  'input/test/collated-files.html',
	  'input/regression/collated-files.html']:
	do_urchin (f)

system ('rsync --delete --stats --progress -pgorltvu -e ssh . %s:/var/www/lilypond/doc/%s/' % (host, dir))

