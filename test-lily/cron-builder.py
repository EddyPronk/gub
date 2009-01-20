#! /usr/bin/env python

# FIXME: replace `lilypond' with $package to make generic tester

def argv0_relocation ():
    import os, sys
    bindir = os.path.dirname (sys.argv[0])
    prefix = os.path.dirname (bindir)
    if not prefix:
        prefix = bindir + '/..'
    sys.path.insert (0, prefix)

argv0_relocation ()

import os
import optparse
import sys
#
from gub import logging
from gub import loggedos

"""
run as

  test-lily/cron-builder.py \
  --test-options "--to me@mydomain.org --from me@mydomain.org --repository . --smtp smtp.xs4all.nl" [PLATFORM]...

"""

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

    p.add_option ('-v', '--verbose', action='count', dest='verbosity',
                  default=0)

    (options, args) = p.parse_args ()
    
    options.make_options += ' LILYPOND_BRANCH=%s' % options.branch

    if '--repository' not in options.test_options:
        options.test_options += ' --repository=downloads/lilypond.git'

    if '--branch' not in  options.test_options:
        branch = options.branch
        local_branch = options.local_branch
        branch_sep = ':'
        
        # FIXME: what happened to branch juggling?
        if 1:
            local_branch = ''
            branch_sep = ''
        options.test_options += (' --branch=lilypond=%(branch)s%(branch_sep)s%(local_branch)s'
                              % locals ())
        
    return (options, args)

def main ():
    (options, args) = parse_options ()
# FIXME: local/system; wow that's from two layout changes ago!
#    os.environ['PATH']= os.getcwd () + '/target/local/system/usr/bin:' + os.environ['PATH']
#    print os.environ['PATH']
    
    os.system ('mkdir -p log')
    if options.dry_run:
        options.verbosity = logging.get_numeric_loglevel ('command')
        
    logging.set_default_log ('log/cron-builder.log', options.verbosity)
    logger = logging.default_logger
    
    logging.info (' *** Starting cron-builder:\n  %s ' % '\n  '.join (args)) 

    if options.clean:
        # FIXME: what if user changes ~/.gubrc?  should use gubb.Settings!
        loggedos.system (logger, 'rm -rf log/ target/ uploads/ buildnumber-* downloads/lilypond-*')

    make_cmd = 'make -f lilypond.make %s ' % options.make_options
    python_cmd = sys.executable  + ' '

    branch = options.branch
    local_branch = options.local_branch
    branch_sep = ':'

    # FIXME: what happened to branch juggling?
    if 1:
        local_branch = ''
        branch_sep = ''

    if 0: #FIXME: use if 1: when --stage download is fixed
        # cannot do this now, --stage=dowload of fontconfig depends on
        # tools freetype-config
        # must build bootstrap first
        
        # FIXME: use gub-tester's download facility
        # can't have these in gub-tester, since these
        # will always usually result in "release already tested"
        for platform in args:
            loggedos.system (logger, python_cmd + 'bin/gub --branch=lilypond=%(local_branch)s%(branch_sep)s:%(branch)s --platform=%(platform)s --stage=download lilypond'
                             % locals ())
            loggedos.system (logger, 'rm -f target/%(platform)s/status/lilypond-%(branch)s*' % locals ())
    else:
        loggedos.system (logger, make_cmd + 'bootstrap')

    test_cmds = []
    if 1:
        test_cmds.append (make_cmd + 'bootstrap')
    if options.build_package:
        test_cmds += [python_cmd + 'bin/gub --branch=lilypond=%(branch)s%(branch_sep)s%(local_branch)s --skip-if-locked --platform=%(platform)s lilypond'
                      % locals () for platform in args]
        
    if options.build_installer:
        version_options = '' 
            
        # installer-builder does not need remote-branch
        test_cmds += [python_cmd + 'bin/gib --skip-if-locked %(version_options)s --branch=lilypond=%(branch)s%(branch_sep)s%(local_branch)s --platform=%(platform)s build-all lilypond'
                      % locals () for platform in args]

    if options.build_docs:
        test_cmds += [make_cmd + 'doc-build',
                      make_cmd + 'doc-export']
        options.test_options += ' --dependent'


    if options.build_tarball:
        test_cmds += [make_cmd + 'dist-check']

    loggedos.system (logger, python_cmd + 'bin/gub-tester %s %s'
            % (options.test_options, ' '.join (["'%s'" % c for c in test_cmds])))

if __name__ == '__main__':
    main ()
