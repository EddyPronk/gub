#!/usr/bin/python
import misc
import re
import sys
import optparse
import os

def parse_options ():
    p = optparse.OptionParser ()
    p.usage = "set-installer-version.py REPO-DIR"
    p.add_option ('--branch',
		  action="store",
		  dest="branch",
                  default="HEAD",
		  help="CVS repository of lilypond.")
    
    p.add_option ('--output',
		  action="store",
		  dest="output",
                  default="VERSION",
		  help="where to write result.")
    
    (o,a) = p.parse_args ()
    if len (a) < 1:
	p.print_help()
	sys.exit (2)
    
    return o,a

    
def get_cvs_version (dir):
    print 'getting version from cvs .. '
    d = misc.grok_sh_variables (dir + '/VERSION')
    return '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
    
def get_git_version (dir, branch):
    print 'getting version from git .. '
    
    cmd = 'git --git-dir %(dir)s/ ' % locals ()
    commit_id = misc.read_pipe ('%(cmd)s log --max-count=1 %(branch)s' % locals ())
    m = re.search ('commit (.*)\n', commit_id)

    commit_id = m.group (1)

    version_id = misc.read_pipe ('%(cmd)s ls-tree %(commit_id)s VERSION' % locals ())
    version_id = version_id.split (' ')[2]
    version_id = version_id.split ('\t')[0]

    version_str = misc.read_pipe ('%(cmd)s cat-file blob %(version_id)s' % locals())

    d = misc.grok_sh_variables_str (version_str)

    return '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d




(o,args) = parse_options ()

version = ''
for a in args:
    if not os.path.isdir (a):
        continue

    if os.path.isdir (a + '/objects'):
        # git:

        version = get_git_version (a, o.branch)
    elif os.path.isdir (a + '/' + o.branch):
        version = get_cvs_version (a + '/' + o.branch)

    if version:
        break

if not version:
    version = '0.0.0'
    
open (o.output, 'w').write (version)
