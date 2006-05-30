#!/usr/bin/python
import sys
import os
import optparse
import re

"""
run as

  python clean-gub-build.py --darcs-upstream http://lilypond.org/~hanwen/gub/ \
  --test-opts "--to me@mydomain.org --from me@mydomain.org --repository . --smtp smtp.xs4all.nl" 

"""

dry_run = False
build_platform = {
	'darwin': 'darwin-ppc',
	'linux2': 'linux',
}[sys.platform]

def parse_options ():
    p = optparse.OptionParser ()

    p.add_option ('--clean',
                  action='store_true',
                  dest='clean',
                  default=False,
                  help="don't do incremental build.")

    p.add_option ('--branch',
                  dest="branch",
                  default="HEAD",
                  action="store",
                  help="")
    

    p.add_option ('--installer',
                  action="store_true",
                  dest="build_installer",
                  default=None,
                  help="build lilypond installer")

    p.add_option ('--docs',
                  action="store_true",
                  dest="build_docs",
                  default=None,
                  help="build docs")
    
    p.add_option ('--package',
                  action="store_true",
                  dest="build_package",
                  default=None,
                  help="build lilypond gup package")

    p.add_option ('--make-options',
                  action='store',
                  dest='make_options',
                  default="",
                  help='what to pass to make')

    p.add_option ('--test-options',
                  action='store',
                  dest='test_options',
                  default="",
                  help='what to pass to test-gub.py')

    p.add_option ('--darcs-upstream',
                  action="store",
                  dest="darcs_upstream",
                  default=None,
                  help="upstream repository")


    p.add_option ('--dry-run',
                  action="store_true",
                  dest="dry_run",
                  default=False,
                  help="test self")

    (opts, args) = p.parse_args ()
    global dry_run
    dry_run = opts.dry_run
    opts.make_options += " BRANCH=%s" % opts.branch

    return (opts, args)


def system (c, ignore_error=False):
    print 'executing' , c

    s = None
    if not dry_run:
        s = os.system (c)
        
    if s and not ignore_error:
        raise 'barf'


def read_make_vars (file):
    d = {}
    for l in open (file).readlines():
        def func(m):
            d[m.group(1)] = m.group(2)
            return ''

        l = re.sub ('^([a-zA-Z0-9_]+) *= *(.*)', func, l)
    return d

def main ():
    (opts,args) = parse_options ()

    if opts.clean:
        system ('rm -rf log/ target/ uploads/ buildnumber-* downloads/lilypond-*')
    if opts.darcs_upstream:
        system ('darcs pull -a ' + opts.darcs_upstream)

    make_cmd = 'make %s ' % opts.make_options
    python_cmd = sys.executable  + ' '
    ## can't have these in test-gub, since these
    ## will always usually result in "release already tested"
    if not os.path.exists ('downloads/lilypond-%s' % opts.branch):
        system (make_cmd + 'bootstrap-download')
    
    system (make_cmd + 'download')

    lily_build_dir = 'target/%s/build/lilypond-%s' %  (build_platform, opts.branch) 
    lily_src_dir = 'target/%s/src/lilypond-%s' % (build_platform, opts.branch) 

    test_cmds = []
    if opts.build_package:
        test_cmds += [python_cmd + 'gub-builder.py --branch %s -lp %s build lilypond ' % (opts.branch, p) for p in args]
    if opts.build_installer:
        build_str = read_make_vars ('buildnumber-%s.make' % opts.branch)['INSTALLER_BUILD']
        version_str = ('%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s'
                       % read_make_vars ('downloads/lilypond-%s/VERSION' % opts.branch))

        test_cmds += [python_cmd + 'installer-builder.py -b %s -v %s --branch %s -p %s build-all lilypond '
                      % (build_str, version_str, opts.branch, p) for p in args]

    if opts.build_docs:
        args = args + ['doc']
        test_cmds += [make_cmd + 'doc-build',
                      python_cmd + 'test-lily/rsync-lily-doc.py '
                      '--recreate '
                      '--output-distance %s/scripts/output-distance.py '
                      ' %s/out-www/web-root ' % (lily_src_dir, lily_build_dir)]

    
    system (python_cmd + 'test-gub.py %s %s '
            % (opts.test_options, ' '.join (["'%s'" % c for c in test_cmds])))

    if opts.build_docs and not opts.clean:

        ## refresh once a day 
        system ("find target/%s/build/lilypond-%s/ -name 'lily-[0-9]*' -mtime +1   -exec rm '{}' ';'" % (build_platform, opts.branch))
        
        ## texi2dvi leaves junk that confuse make. FIXME
        system ("rm -f target/%s/build/lilypond-%s/Documentation/user/out-www/{lilypond,lilypond-internals,music-glossary}.*" % (build_platform, opts.branch))
        
if __name__ == '__main__':
    main ()


    
                      
