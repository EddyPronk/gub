#!/usr/bin/python
import os
import re
import sys
import string

import optparse

################
# settings

def parse_options ():
    p = optparse.OptionParser ()
    p.add_option ('--upload',
		  dest='destination',
		  help='where to upload the result',
		  default='hanwen@ssh.webdev.nl:/var/www/lilypond/doc')

    home = os.environ['HOME']
    p.add_option ('--unpack-dir',
		  dest='unpack_dir',
		  default=home + '/nobackup/lilypond-local-web/doc'
		  help="Where to put local versions of the docs")

    (opts, args) = p.parse_args ()
    return (opts, args)

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

def read_version (source):
    return tuple (open (source + '/VERSION').read ().split ('.'))
    
def create_local_web_dir (options, source):
    os.chdir (options.unpack_dir)

    version = read_version (source)
    dir = 'v%s' % '.'.join (version)
    
    system ('rm -rf %s' % dir)
    system ('mkdir -p %s' % dir)
    os.chdir (dir)
    
    system ('rsync -a %s/ . ' % webroot)
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


def upload (options, source):
    os.chdir (options.unpack_dir)
    version = read_version (source)

    dir = 'v%s' % '.'.join (version)
    os.chdir (dir)
    branch_dir = 'v%s.%s' % '.'.join (version[:2])
    system ('rsync --delete --stats --progress -pgorltvu -e ssh . %s/%s/' % (options.destination, branch_dir))
    
    
def main ():
    (opts, args) = parse_options ()

    for a in args:
	create_local_web_dir (opts, a)
	if opts.destination:
	    upload (opts, a)


if __name__ == '__main__':
    main ()
