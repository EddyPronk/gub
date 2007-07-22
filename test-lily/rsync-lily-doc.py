#!/usr/bin/python

import os
import re
import sys
import string
import glob
import optparse

sys.path.insert (0, os.path.split (sys.argv[0])[0] + '/..')

from gub import versiondb

################
# settings
# 'hanwen@ssh.webdev.nl:/var/www/lilypond/doc'
def parse_options ():
    home = os.environ['HOME']

    p = optparse.OptionParser ()
    p.add_option ('--upload',
		  dest='destination',
		  help='where to upload the result',
		  default='')
    p.add_option ('--dbfile',
		  dest='dbfile',
		  help='which version db to use',
		  default='uploads/lilypond.versions')
    p.add_option ('--output-distance',
                  dest="output_distance_script",
                  help="compute signature distances using script") 
    p.add_option ("--dry-run",
                  action="store_true",
                  dest="dry_run",
                  default=False,
                  help="don't actually run any commands.")
    p.add_option ("--version-file",
                  action="store",
                  dest="version_file",
                  help="where to get the version number")
    p.add_option ('--recreate',
                  dest="recreate",
                  action="store_true",
                  help="rebuild webdirectory. Discards test-results.") 
    p.add_option ('--unpack-dir',
		  dest='unpack_dir',
		  default='uploads/webdoc/',
		  help="Where to put local versions of the docs")
    p.add_option ('--test-dir',
		  dest='test_dir',
		  default='uploads/webtest/',
		  help="Where to put local versions of the docs")
    p.add_option ('--upload-dir',
		  dest='upload_dir',
		  default='uploads/',
		  help="Where to put local versions of the docs")

    (opts, args) = p.parse_args ()

    opts.unpack_dir = os.path.abspath (opts.unpack_dir)
    if opts.output_distance_script:
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
    s = open (source).read ()
    s = s.strip()
    return tuple (s.split ('.'))
    
def create_local_web_dir (options, source):
    if not os.path.isdir (options.unpack_dir):
        system ('mkdir -p '  + options.unpack_dir)

    print 'creating web root in',  options.unpack_dir 
    os.chdir (options.unpack_dir)

    dir = 'v%s' % '.'.join (options.version)
    
    system ('rm -rf %s' % dir)
    system ('mkdir -p %s' % dir)
    os.chdir (dir)
    
    system ('rsync -Wa %s/ . ' % source)

    if options.dry_run:
        return
    
    print 'Instrumenting for Google Analytics' 
    for f in ['Documentation/index.html',
	      'Documentation/topdocs/NEWS.html',
	      'Documentation/user/lilypond/index.html',
	      'Documentation/user/lilypond-internals/index.html',
	      'examples.html',
	      'Documentation/user/music-glossary/index.html',
	      'Documentation/topdocs/NEWS.html',
	      'Documentation/user/lilypond/Tutorial.html',
#	      'input/test/collated-files.html',
	      'input/regression/collated-files.html']:
        do_urchin (f)

def compare_test_tarballs (options, version_file_tuples):
    (version, build), last_file = version_file_tuples[-1]
    dest_dir = '%s/v%s-%d' % (options.test_dir,
                              '.'.join (map (str, version)),
                              build)

    dest_dir = os.path.abspath(dest_dir)
    if not os.path.isdir (dest_dir):
        os.makedirs (dest_dir)

    dirs = []
    version_strs = []
    unpack_dir = os.path.abspath(dest_dir) + '-unpack'
    
    for (tup, file) in version_file_tuples:
        version, build = tup
        version_str = '%s-%d' % ('.'.join(map (str, version)), build)
        version_strs.append (version_str)
        dir_str = 'v' + version_str
        dirs.append (dir_str)

        dir_str = unpack_dir + '/' + dir_str
        if os.path.exists (dir_str):
            system ('rm -rf %s' % dir_str)
        os.makedirs (dir_str)
        system ('tar --strip-component=3 -C %s -xjf %s' % (dir_str, file))

    html = ''
    for d in dirs[:-1]:
        cmd = ('cd %s && python %s --create-images --output-dir %s/compare-%s --local-datadir %s %s '
               % (unpack_dir,
                  options.output_distance_script,
                  dest_dir, d, d, dirs[-1]))
        html += '<li><a href="compare-%(d)s/index.html">results for %(d)s</a>' % locals()
        system(cmd)

    if html:
        html = '<ul>%(html)s</ul>' % locals ()
    else:
        html = 'no previous versions to compare with'

    version_str = version_strs[-1]
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

    system ('rm -rf %(unpack_dir)s' % locals ())
    
    open (dest_dir + '/test-results.html', 'w').write (html)

def compare_test_info (options):
    outputs = glob.glob(options.upload_dir + '/lilypond-*.test-output*')

    current_version = tuple (map (int, options.version))
    db = versiondb.VersionDataBase (options.dbfile)
    current_build = db.get_next_build_number (current_version)
    current_tuple = (current_version, current_build)

    versions_found = []
    current_test_output = ''
    for f in outputs:
        m = re.search ('lilypond-([.0-9]+)-([0-9]+).test-output.tar.bz2', f)
        assert m

        version = map (int, m.group (1).split ('.'))
        build = int (m.group (2))
        tup = (version, build)
        
        if tup <= current_tuple:
           versions_found.append ((tup, f))

    versions_found.sort()
    compare_test_tarballs (options, versions_found[-3:])

# deprecated
def compute_distances (options, source):
    os.chdir (options.unpack_dir)
    cur_version = tuple (map (int, options.version))
    region = 3

    versions = [(cur_version[0], cur_version[1], cur_version[2] - i) for i in range (1, region + 1)]
    version_dirs = ['v%d.%d.%d' % v for v in versions]
    version_str = '%d.%d.%d'  % cur_version

    if cur_version[1] % 2 == 1:
        stable_major = cur_version[1] - 1

        stable_dirs = glob.glob ('v%d.%d.*' % (cur_version[0], stable_major))
                        
        if stable_dirs:
            def dir2number (m):
                return tuple (map (int, m.groups ())) + (m.group (0),)
            
            stable_dirs = [dir2number (re.search ('v([0-9]+)[.]([0-9]+)[.]([0-9]+)', s))
                           for s in stable_dirs]
            stable_dirs.sort ()
            stable_dirs.reverse ()
            stable_dirs = [t[-1] for t in stable_dirs]
            version_dirs.append (stable_dirs[0])

    version_dirs = [d for d in version_dirs if
                    os.path.isdir (os.path.join (options.unpack_dir, d))]

    cur_dir = 'v' + version_str

    html = ''
    for d in version_dirs:
        cmd = 'python %s %s %s ' % (options.output_distance_script,
                                    d, cur_dir)

        base = os.path.split (d)[1]

        html += '<li><a href="compare-%(base)s/index.html">results for %(base)s</a>' % locals()
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

    dir = 'v%s' % '.'.join (options.version)
    os.chdir (dir)

    system ('chmod -R g+w . ' )
    system ('chgrp -R lilypond . ' )
    system ('chmod 2775 `find -type d ` . ')
    branch_dir = 'v%s.%s' % (options.version[:2])
    system ('rsync --exclude "*.signature" --hard-links --delay-updates --delete --delete-after --stats --progress -pgorltvu -e ssh . %s/%s/' % (options.destination, branch_dir))
    
    
def main ():
    (opts, args) = parse_options ()

    opts.version  = read_version (opts.version_file)
    
    for a in args:
        a = os.path.abspath (a)

        if opts.dry_run:
            def my_system (x):
                print x
            global system
            system = my_system

        if opts.recreate:
            create_local_web_dir (opts, a)
        if opts.output_distance_script:
            compare_test_info (opts)
	if opts.destination:	
            upload (opts, a)


if __name__ == '__main__':
    main ()
