#! /usr/bin/python

import sys
import os
import optparse
import re
import fcntl
import time

"""
run as

  python test-lily/cron-builder.py \
  --test-opts "--to me@mydomain.org --from me@mydomain.org --repository . --smtp smtp.xs4all.nl" [PLATFORM]...

"""

dry_run = False
build_platform = {
	'darwin': 'darwin-ppc',
	'linux2': 'linux-x86',
}[sys.platform]

################################################################
# UGh , cut & paste
class LogFile:
    def __init__ (self, name):
        self.file = open (name, 'a')
        self.prefix = 'cron-builder.py[%d]: ' % os.getpid ()

    def log (self, msg):
        self.file.write ('%s%s\n' % (self.prefix, msg))
        self.file.flush ()
        
    def __del__ (self):
        self.log (' *** finished')

log_file = None

def parse_options ():
    p = optparse.OptionParser ()

    p.add_option ('--clean',
                  action='store_true',
                  dest='clean',
                  default=False,
                  help="don't do incremental build.")

    p.add_option ('--local-branch',
                  dest="local_branch",
                  default="master-git.sv.gnu.org-lilypond.git",
                  action="store",
                  help="which branch of lily to build")

    p.add_option ('--branch',
                  dest="branch",
                  default="master",
                  action="store",
                  help="which branch of lily to build")

    p.add_option ('--installer',
                  action="store_true",
                  dest="build_installer",
                  default=None,
                  help="build lilypond installer")

    p.add_option ('--docs',
                  action="store_true",
                  dest="build_docs",
                  default=None,
                  help="build docs. Implies --dependent for gub-tester")
    
    p.add_option ('--package',
                  action="store_true",
                  dest="build_package",
                  default=None,
                  help="build lilypond gup package")

    p.add_option ('--tarball',
                  action="store_true",
                  dest="build_tarball",
                  default=None,
                  help="build and check lilypond source tarball")

    p.add_option ('--make-options',
                  action='store',
                  dest='make_options',
                  default="",
                  help='what to pass to make')

    p.add_option ('--test-options',
                  action='store',
                  dest='test_options',
                  default="",
                  help='what to pass to gub-tester')

    p.add_option ('--unversioned',
                  action="store_true",
                  dest="unversioned",
                  default=False,
                  help="produce 0.0.0-0 binary") 

    p.add_option ('--dry-run',
                  action="store_true",
                  dest="dry_run",
                  default=False,
                  help="test self")

    (opts, args) = p.parse_args ()
    
    global dry_run
    dry_run = opts.dry_run
    opts.make_options += " BRANCH=%s" % opts.branch

    if '--repository' not in  opts.test_options:
        opts.test_options += ' --repository=downloads/lilypond.git '

    if '--branch' not in  opts.test_options:
        opts.test_options += (' --branch=lilypond=%s:%s'
                              % (opts.branch, opts.local_branch))
        
    return (opts, args)

def system (c, ignore_error=False):
    log_file.log ('executing %s' % c)

    s = None
    if not dry_run:
        s = os.system (c)
        
    if s and not ignore_error:
        raise 'barf'

def main ():
    (opts, args) = parse_options ()
    os.environ['PATH']= os.getcwd () + '/target/local/system/usr/bin:' + os.environ['PATH']
    print os.environ['PATH']
    global log_file
    
    os.system ('mkdir -p log')
    log_file = LogFile ('log/cron-builder.log')
    log_file.log (' *** %s' % time.ctime ())
    log_file.log (' *** Starting cron-builder:\n  %s ' % '\n  '.join (args)) 

    if opts.dry_run:
        log_file.file = sys.stdout

    if opts.clean:
        system ('rm -rf log/ target/ uploads/ buildnumber-* downloads/lilypond-*')

    make_cmd = 'make %s ' % opts.make_options
    python_cmd = sys.executable  + ' '

    # FIXME: use gub-tester's download facility
    ## can't have these in gub-tester, since these
    ## will always usually result in "release already tested"
    for a in args:
        system (python_cmd + 'bin/gub --branch %s:%s -p %s --stage=download lilypond'
                % (opts.branch, opts.local_branch, a))
        system ('rm -f target/%s/status/lilypond-%s*' % (a, opts.branch))

    test_cmds = []
    if opts.build_package:
        test_cmds += [python_cmd + 'bin/gub --branch %s:%s -lp %s lilypond '
                      % (opts.branch, opts.local_branch, p) for p in args]
        
    if opts.build_installer:
        version_opts = '' 
            
        test_cmds += [python_cmd + 'bin/installer-builder --skip-if-locked %s --branch %s -p %s build-all lilypond '
                      % (version_opts, opts.local_branch, p) for p in args]

    if opts.build_docs:
        test_cmds += [make_cmd + 'doc-build',
                      make_cmd + 'doc-export']
        opts.test_options += ' --dependent '


    if opts.build_tarball:
        test_cmds += [make_cmd + " dist-check"]

    system (python_cmd + 'bin/gub-tester %s %s '
            % (opts.test_options, ' '.join (["'%s'" % c for c in test_cmds])))

if __name__ == '__main__':
    main ()
