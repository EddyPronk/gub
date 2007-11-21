#!/usr/bin/python

import os
import re
import sys
import string
import glob
import optparse

sys.path.insert (0, os.path.split (sys.argv[0])[0] + '/..')

from gub import versiondb

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
                  dest='output_distance_script',
                  help='compute signature distances using script') 
    p.add_option ('--dry-run',
                  action='store_true',
                  dest='dry_run',
                  default=False,
                  help='do not actually run any commands.')
    p.add_option ('--version-file',
                  action='store',
                  dest='version_file',
                  help='where to get the version number')
    p.add_option ('--test-dir',
		  dest='test_dir',
		  default='uploads/webtest/',
		  help='Where to put local versions of the test output')
    p.add_option ('--upload-dir',
		  dest='upload_dir',
		  default='uploads/',
		  help='Where to find test-output tarballs')

    (options, args) = p.parse_args ()

    if options.output_distance_script:
        options.output_distance_script = os.path.abspath (options.output_distance_script)

    return (options, args)

## UGH C&P
def system (cmd):
    print cmd
    stat = os.system (cmd)
    if stat:
    	raise 'fail'
def read_version (source):
    s = open (source).read ()
    s = s.strip()
    return tuple (s.split ('.'))
## end C&P
    

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
    
    open (dest_dir + '/index.html', 'w').write (html)

def compare_test_info (options):
    outputs = glob.glob(options.upload_dir + '/lilypond-*.test-output*')

    current_version = tuple (map (int, options.version))
    current_tuple = (current_version, options.build)

    versions_found = []
    current_test_output = ''
    for f in outputs:
        m = re.search ('lilypond-([.0-9]+)-([0-9]+).test-output.tar.bz2', f)
        if not m:
            print f
            assert 0

        version = map (int, m.group (1).split ('.'))
        build = int (m.group (2))
        tup = (version, build)
        
        if tup <= current_tuple:
           versions_found.append ((tup, f))

    versions_found.sort()
    compare_test_tarballs (options, versions_found[-3:])

def upload (options):
    os.chdir (options.test_dir)

    target = 'v%s-%d' % ('.'.join (options.version),
                         options.build)
    os.chdir(target)
    
    system ('chmod -R g+w .')
    system ('chgrp -R lilypond .' )
    system ('chmod 2775 `find -type d ` .')
    system ('rsync --hard-links --delay-updates --delete --delete-after --stats --progress -pgorltvu -e ssh . %s/%s/' % (options.destination, target))
    
    
def main ():
    (options, args) = parse_options ()

    options.version  = read_version (options.version_file)
    db = versiondb.VersionDataBase (options.dbfile)
    options.build = db.get_next_build_number (options.version)
    
    if options.dry_run:
        def my_system (x):
            print x
        global system
        system = my_system

    if options.output_distance_script:
        compare_test_info (options)
    if options.destination:
        upload (options)


if __name__ == '__main__':
    main ()
