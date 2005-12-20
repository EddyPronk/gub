#!/usr/bin/python

'''
  xpm - Keep GUB root up to date
  
  License: GNU GPL
'''

import __main__
import getopt
import os
import re
import string
import sys

sys.path.insert (0, 'specs/')

import framework
import gub
import settings as settings_mod
import xpm

def psort (lst):
	plist.sort (lst)
	return lst
#urg
plist = list

def usage ():
	sys.stdout.write ('''%s [OPTION]... COMMAND [PACKAGE]...

Commands:
''' % basename)
	d = __main__.__dict__
	commands = filter (lambda x:
			   type (d[x]) == type (usage) and d[x].__doc__, d)
	sys.stdout.writelines (map (lambda x:
				    "    %s - %s\n" % (x, d[x].__doc__),
			       psort (commands)))
	sys.stdout.write (r'''
Options:
    -h,--help              show brief usage
    -m,--mirror=URL        use mirror [%(mirror)s]
    -n,--name              print package name only
    -p,--platform=NAME     set platform [%(platform)s]
    -r,--root=DIR          set %(PLATFORM)s root [%(ROOT)s]
    -t,--tools             manage tools
    -x,--no-deps           ignore dependencies

Defaults are taken from ./%(rc_file)s
    
''' % d)

arguments = 0
def help ():
	'''help COMMAND'''
	if len (arguments) < 1:
		usage ()
		sys.exit ()

	print  __main__.__dict__[packagename].__doc__

def find ():
	'''package containing file'''
	global packagename
	regexp = re.sub ('^%s/' % ROOT, '/', packagename)
	hits = []
	for packagename in psort (map (gub.Package.name,
				       pm.installed_packages ())):
		for i in pm.name_files (packagename):
			if re.search (regexp, '/%s' % i):
				hits.append ('%s: /%s' % (packagename, i))
	print (string.join (hits, '\n'))



def read_xpm_rc ():
	if os.path.exists (rc_file):
		print 'reading', rc_file
		h = open (rc_file)
		for i in h.readlines ():
			k, v = i.split ('=', 2)
			if k in rc_options:
				__main__.__dict__[k] = eval (v)

def write_xpm_rc ():
	"Write defaults in .xpm-apt.rc. "
	h = open (rc_file, 'w')
	print 'writing', rc_file
	for i in rc_options:
		h.write ('%s="%s"\n' % (i, __main__.__dict__[i]))
	h.close ()


CWD = os.getcwd ()
basename = os.path.basename (sys.argv[0])
xpm_rc = CWD + '/.' + basename
platform = ''
PLATFORM = ''
ROOT = ''
distname = 'unused'
config = ROOT + '/etc/xpm'
mirror = 'file://uploads/gub'

rc_options = ['platform', 'PLATFORM', 'ROOT', 'mirror', 'distname']
rc_file = '.xpm-apt.rc'

read_xpm_rc ()

def do_options ():
	global command, mirror, ROOT, PLATFORM, platform, packagename
	global arguments, platform, name_p, nodeps_p, tool_p
	(options, arguments) = getopt.getopt (sys.argv[1:],
					  'hm:np:r:tx',
					  ('help', 'mirror=', 'name',
					   'no-deps', 'root=', 'tool'))

	command = 'help'
	packagename = 0
	if len (arguments) > 0:
		command = arguments.pop (0)

	if arguments and arguments[0] == 'all':
		arguments = m._packages.keys()
		
	if len (arguments) > 0:
	       	packagename = arguments[0]

	tool_p = 0
	name_p = 0
	nodeps_p = 0
	for i in options:
		o = i[0]
		a = i[1]

		if 0:
			pass
		elif o == '--help' or o == '-h':
			command = 'help'
		elif o == '--mirror' or o == '-m':
			mirror = a
		elif o == '--root' or o == '-r':
			ROOT = a
		elif o == '--tool' or o == '-t':
			tool_p = 1
		elif o == '--platform' or o == '-p':
			platform = a
			PLATFORM = {
				'darwin': 'powerpc-apple-darwin7',
				'mingw': 'i686-mingw32',
				'linux': 'linux',
				}[a]
			ROOT = 'target/%(PLATFORM)s/system' % globals ()
		elif o == '--name' or o == '-n':
			name_p = 1
		elif o == '--no-deps' or o == '-x':
			nodeps_p = 1

pm = None

def install ():
	'''download and install packages with dependencies'''
	for p in arguments:
		if pm.name_is_installed (p):
			print '%s already installed' % p

	for p in arguments:
		if not pm.name_is_installed (p):
			if nodeps_p:
				pm.install_single_package (pm._packages[p])
			else:
				pm.install_package (pm._packages[p])

def remove ():
	'''uninstall packages'''
	for p in arguments:
		if not pm.name_is_installed (p):
			raise '%s not installed' % p

	for p in arguments:
		pm.name_uninstall (p)

def list ():
	'''installed packages'''
	if name_p:
		print '\n'.join (psort (map (gub.Package.name,
					     pm.installed_packages ())))
	else:
		print '\n'.join (psort (map (lambda x: '%-20s%s' % (x.name (),
							     x.full_version ()),
					     pm.installed_packages ())))


def available ():
	print '\n'.join (pm._packages.keys ())

def files ():
	'''list installed files'''
	for p in arguments:
		if not pm.name_is_installed (p):
			print '%s not installed' % p
		else:
			print '\n'.join (pm.name_files (p))

def main ():
	global pm
	do_options ()

	settings = settings_mod.Settings (PLATFORM)
	settings.platform = platform

	target_manager = xpm.Package_manager (settings.system_root)
	tool_manager = xpm.Package_manager (settings.tooldir)


	## ugh : code dup. 
	if tool_p:
		if platform == 'darwin':
			import darwintools
			map (tool_manager.register_package,
			     darwintools.get_packages (settings))
		if platform.startswith ('mingw'):
			import mingw
			map (tool_manager.register_package,
			     mingw.get_packages (settings))
		pm = tool_manager
	else:
		pm = target_manager
		
	map (pm.register_package,
	     framework.get_packages (settings))
	# ugh
	pm.resolve_dependencies ()

	if command:
		if command in __main__.__dict__:
			__main__.__dict__[command] ()
		else:
			sys.stderr.write ('no such command: ' + command)
			sys.stderr.write ('\n')
			sys.exit (2)

if __name__ == '__main__':
	main ()
