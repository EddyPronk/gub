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

    
def get_cvs_version (dir, branch):
    f = dir + '/' + branch + '/VERSION'
    print 'getting version from cvs .. ' , f
    d = misc.grok_sh_variables (f)
    return '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
    
def get_git_version (dir, branch):
    print 'getting version from git .. '
    
    cmd = 'git --git-dir %(dir)s/ ' % locals ()
    commit_id = misc.read_pipe ('%(cmd)s log --max-count=1 %(branch)s'
                                % locals ())
    m = re.search ('commit (.*)\n', commit_id)
    commit_id = m.group (1)
    version_id = misc.read_pipe ('%(cmd)s ls-tree %(commit_id)s VERSION'
                                 % locals ())
    version_id = version_id.split (' ')[2]
    version_id = version_id.split ('\t')[0]

    version_str = misc.read_pipe ('%(cmd)s cat-file blob %(version_id)s'
                                  % locals())
    d = misc.grok_sh_variables_str (version_str)
    return '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d

def scm_flavor (dir, branch):
    if os.path.isdir (dir + '/objects'):
        return 'git'
    if os.path.isdir (dir + '/' + branch + '/CVS'):
        return 'cvs'
    return None

def version_from_scm_dir (dir, branch):
    flavor = scm_flavor (dir, branch)
    if flavor == 'git':
        return get_git_version (dir, branch)
    elif flavor == 'cvs':
        return get_cvs_version (dir, branch)
    return None

def main ():
    (o, dirs) = parse_options ()

    for dir in dirs:
        version = version_from_scm_dir (dir, o.branch)
        if version:
            break

    if not version:
        version = '0.0.0'

    print 'found version', version
    open (o.output, 'w').write (version)

if __name__ == '__main__':
    main ()
