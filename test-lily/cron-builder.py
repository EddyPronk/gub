#!/usr/bin/python
import sys
import os
import optparse

"""
run as

  python clean-gub-build.py --darcs-upstream http://lilypond.org/~hanwen/gub/ \
  --test-opts "--to hanwen@xs4all.nl --to janneke-list@xs4all.nl --smtp smtp.xs4all.nl" 


This script will setup local distcc on ports 3633 and 3634. Do not run
unless behind a firewall.

"""
test_self = False

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
    
    p.add_option ('--package-only',
                  action="store_true",
                  dest="package_only",
                  default=None,
                  help="only build lilypond package")

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


    p.add_option ('--test-self',
                  action="store_true",
                  dest="test_self",
                  default=False,
                  help="test self")

    (opts, args) = p.parse_args ()
    global test_self
    test_self = opts.test_self
    opts.make_options += " BRANCH=%s" % opts.branch

    return (opts, args)


def system (c, ignore_error=False):
    print 'executing' , c

    s = None
    if not test_self:
        s = os.system (c)
        
    if s and not ignore_error:
        raise 'barf'

def main ():
    (opts,args) = parse_options ()

    if opts.clean:
        system ('rm -rf log/ target/ uploads/ buildnumber-* downloads/lilypond-*')
    if opts.darcs_upstream:
        system ('darcs pull -a ' + opts.darcs_upstream)

    test_cmds = []
    if opts.package_only:
        test_platforms = ['python gub-builder.py --branch %s -lp %s build lilypond ' % (opts.branch, p) for p in args]
        test_cmds = ['make %s download' % opts.make_options] + test_platforms
    else:
        args = ['bootstrap-download', 'bootstrap'] + args + ['doc']
        test_cmds = ['make %s %s' % (opts.make_options, p) for p in args]

    system ('python test-gub.py %s %s '
            % (opts.test_options, ' '.join (["'%s'" % c for c in test_cmds])))

    
if __name__ == '__main__':
    main ()


    
                      
