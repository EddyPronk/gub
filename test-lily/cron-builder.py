#! /usr/bin/python

# FIXME: replace `lilypond' with $package to make generic tester

import os
import optparse
import sys

sys.path.insert (0, os.path.split (sys.argv[0])[0] + '/..')
from gub import oslog

"""
run as

  test-lily/cron-builder.py \
  --test-options "--to me@mydomain.org --from me@mydomain.org --repository . --smtp smtp.xs4all.nl" [PLATFORM]...

"""

dry_run = False
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

    p.add_option ('-v', '--verbose', action='count', dest='verbose', default=0)

    (options, args) = p.parse_args ()
    
    global dry_run
    dry_run = options.dry_run
    options.make_options += " BRANCH=%s" % options.branch

    if '--repository' not in options.test_options:
        options.test_options += ' --repository=downloads/lilypond.git '

    if '--branch' not in  options.test_options:
        options.test_options += (' --branch=lilypond=%s:%s'
                              % (options.branch, options.local_branch))
        
    return (options, args)

def main ():
    (options, args) = parse_options ()
# FIXME: local/system; wow that's from two layout changes ago!
#    os.environ['PATH']= os.getcwd () + '/target/local/system/usr/bin:' + os.environ['PATH']
#    print os.environ['PATH']
    global log_file
    
    os.system ('mkdir -p log')
    if options.dry_run:
        options.verbose = oslog.level['command']
    log_file = oslog.Os_commands ('log/cron-builder.log', options.verbose,
                                  dry_run)
    log_file.info (' *** Starting cron-builder:\n  %s ' % '\n  '.join (args)) 

    if options.clean:
        # FIXME: what if user changes ~/.gubrc?  should use gubb.Settings!
        log_file.system ('rm -rf log/ target/ uploads/ buildnumber-* downloads/lilypond-*')

    make_cmd = 'make -f lilypond.make %s ' % options.make_options
    python_cmd = sys.executable  + ' '

    # FIXME: use gub-tester's download facility
    ## can't have these in gub-tester, since these
    ## will always usually result in "release already tested"
    for a in args:
        log_file.system (python_cmd + 'bin/gub --branch=lilypond=%s:%s -p %s --stage=download lilypond'
                % (options.branch, options.local_branch, a))
        log_file.system ('rm -f target/%s/status/lilypond-%s*' % (a, options.branch))

    test_cmds = []
    if 1:
        test_cmds.append (make_cmd + 'bootstrap')
    if options.build_package:
        test_cmds += [python_cmd + 'bin/gub --branch=lilypond=%s:%s -lp %s lilypond '
                      % (options.branch, options.local_branch, p) for p in args]
        
    if options.build_installer:
        version_options = '' 
            
        test_cmds += [python_cmd + 'bin/installer-builder --skip-if-locked %s  --branch=lilypond=%s:%s -p %s build-all lilypond '
                      % (version_options, options.branch, options.local_branch, p) for p in args]

    if options.build_docs:
        test_cmds += [make_cmd + 'doc-build',
                      make_cmd + 'doc-export']
        options.test_options += ' --dependent '


    if options.build_tarball:
        test_cmds += [make_cmd + " dist-check"]

    log_file.system (python_cmd + 'bin/gub-tester %s %s '
            % (options.test_options, ' '.join (["'%s'" % c for c in test_cmds])))

if __name__ == '__main__':
    main ()
