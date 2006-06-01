#!/usr/bin/python

import os
import re
import sys
import string
import glob
import optparse

################
# settings
# 'hanwen@ssh.webdev.nl:/var/www/lilypond/doc'
def parse_options ():
    p = optparse.OptionParser ()
    p.add_option ('--upload',
		  dest='destination',
		  help='where to upload the result',
		  default='')
    p.add_option ('--output-distance',
                  dest="output_distance_script",
                  help="compute signature distances using script") 

    p.add_option ('--recreate',
                  dest="recreate",
                  action="store_true",
                  help="rebuild webdirectory. Discards test-results.") 

    home = os.environ['HOME']
    p.add_option ('--unpack-dir',
		  dest='unpack_dir',
		  default='uploads/webdoc/',
		  help="Where to put local versions of the docs")

    (opts, args) = p.parse_args ()

    opts.unpack_dir = os.path.abspath (opts.unpack_dir)
    opts.output_distance_script = os.path.abspath (opts.output_distance_script)

    if not args:
        p.print_help()
    
    return (opts, args)

def do_urchin (filename):
    s = open (filename).read()
    if re.search ('UA-68969', s):
    	return
    
    print filename
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
    s = open (source + '/VERSION').read ()
    s = s.strip()
    return tuple (s.split ('.'))
    
def create_local_web_dir (options, source):

    if not os.path.isdir (options.unpack_dir):
        system ('mkdir -p '  + options.unpack_dir)

    print 'creating web root in',  options.unpack_dir 
    os.chdir (options.unpack_dir)

    version = read_version (source)
    dir = 'v%s' % '.'.join (version)
    
    system ('rm -rf %s' % dir)
    system ('mkdir -p %s' % dir)
    os.chdir (dir)
    
    system ('rsync -Wa %s/ . ' % source)

    print 'Instrumenting for Google Analytics' 
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

def compute_distances (options, source):
    os.chdir (options.unpack_dir)

    
    cur_version = tuple (map (int, read_version (source)))
    region = 3

    versions = [(cur_version[0], cur_version[1], cur_version[2] - i) for i in range (1, region + 1)]
    version_dirs = ['v%d.%d.%d' % v for v in versions]
    version_str = '%d.%d.%d'  % cur_version

    if cur_version[1] % 2 == 1:
        stable_major = cur_version[1] - 1

        stable_dirs = glob.glob ('v%d.%d.*' % (cur_version[0], stable_major))

        if stable_dirs:
            stable_dirs.sort ()
            stable_dirs.reverse ()
            version_dirs.append (stable_dirs[0])

    version_dirs = [d for d in version_dirs if
                    os.path.isdir (os.path.join (options.unpack_dir, d))]

    cur_dir = 'v' + version_str

    html = ''
    for d in version_dirs:
        cmd = 'python %s %s %s ' % (options.output_distance_script,
                                    d, cur_dir)

        base = os.path.split (d)[1]

        html += '<li><a href="%(base)s.html">results for %(base)s</a>' % locals()
        system (cmd)

    if html:
        html = '<ul>%(html)s</ul>' % locals ()
    else:
        html = 'no previous versions to compare with'
        
        
    html = '''<html>
<head>
<title>
Regression test results for %(version_str)s
</title>
</head>
<body>
<h1>Regression test results</h1>

%(html)s
</body>
</html>
''' % locals() 
    
    open (cur_dir + '/test-results.html', 'w').write (html)

def upload (options, source):
    os.chdir (options.unpack_dir)

    version = read_version (source)
    dir = 'v%s' % '.'.join (version)
    os.chdir (dir)

    system ('chmod -R g+w . ' )
    system ('chgrp -R lilypond . ' )
    system ('chmod 2755 `find -type d ` . ')
    branch_dir = 'v%s.%s' % (version[:2])
    system ('rsync --delete --stats --progress -pgorltvu -e ssh . %s/%s/' % (options.destination, branch_dir))
    
    
def main ():
    (opts, args) = parse_options ()

    for a in args:
        a = os.path.abspath (a)
        
        if opts.recreate:
            create_local_web_dir (opts, a)
        if opts.output_distance_script:
            compute_distances (opts, a)
	if opts.destination:
	    upload (opts, a)


if __name__ == '__main__':
    main ()
