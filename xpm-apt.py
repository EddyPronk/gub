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
    -r,--root=DIR          set %(PLATFORM)s root [%(ROOT)s]
    -p,--platform=NAME     set platform [%(platform)s]
    -x,--no-deps           ignore dependencies
''' % d)

arguments = 0
def help ():
	'''help COMMAND'''
	if len (arguments) < 2:
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
		for i in pm.file_list_of_name (packagename):
			if re.search (regexp, '/%s' % i):
				hits.append ('%s: /%s' % (packagename, i))
	print (string.join (hits, '\n'))


CWD = os.getcwd ()
basename = os.path.basename (sys.argv[0])
xpm_rc = CWD + '/.' + basename
platform = 'mingw'
PLATFORM = 'i686-mingw32'
ROOT = 'target/%(PLATFORM)s/system' % locals ()

config = ROOT + '/etc/xpm'
mirror = 'file://uploads/gub'

rc_options = ['PLATFORM', 'ROOT', 'mirror', 'distname']
def read_xpm_rc ():
	h = 0
	if os.path.exists (cwd_cyg_apt_rc):
		h = open (cwd_cyg_apt_rc)
		for i in h.readlines ():
			k, v = i.split ('=', 2)
			if k in rc_options:
				__main__.__dict__[k] = eval (v)
		h.close ()

def write_xpm_rc ():
	h = open (cyg_apt_rc, 'w')
	for i in rc_options:
		h.write ('%s="%s"\n' % (i, __main__.__dict__[i]))
	h.close ()

def do_options ():
	global command, mirror, ROOT, PLATFORM, platform, packagename, nodeps_p
	global arguments, platform
	(options, arguments) = getopt.getopt (sys.argv[1:],
					  'hm:p:r:x',
					  ('help', 'mirror=', 'root=', 'no-deps'))

	command = 'help'
	packagename = 0
	if len (arguments) > 0:
		command = arguments.pop (0)

	if arguments and arguments[0] == 'all':
		arguments = m.known_packages.keys()
		
	if len (arguments) > 0:
	       	packagename = arguments[0]

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
		elif o == '--platform' or o == '-p':
			platform = a
			PLATFORM = {
				'darwin': 'powerpc-apple-darwin7',
				'mingw': 'i686-mingw32',
				'linux': 'linux',
				}[a]
			ROOT = 'target/%(PLATFORM)/system' % locals ()
		elif o == '--no-deps' or o == '-x':
			nodeps_p = 1

pm = None

def install ():
	'''download and install packages with dependencies'''
	for p in arguments:
		if pm.is_name_installed (p):
			print '%s already installed' % p

	for p in arguments:
		if not pm.is_name_installed (p):
			pm.install_named (p)

def remove ():
	'''uninstall packages'''
	for p in arguments:
		if not pm.is_name_installed (p):
			raise '%s not installed' % p

	for p in arguments:
		pm.uninstall_named (p)

def list ():
	'''installed packages'''
	print '\n'.join (map (gub.Package.name,
			      psort (pm.installed_packages ())))

def available ():
	print '\n'.join (pm.known_packages.keys ())

def files ():
	'''list installed files'''
	for p in arguments:
		if not pm.is_name_installed (p):
			print '%s not installed' % p
		else:
			print '\n'.join (pm.file_list_of_name(p))

def main ():
	global pm
	do_options ()

	settings = settings_mod.Settings (PLATFORM)
	settings.manager = None
	settings.platform = platform

	target_manager = xpm.Package_manager (settings.system_root)
	##tool_manager = xpm.Package_manager (settings.tooldir)

	map (target_manager.register_package, framework.get_packages (settings))

	pm = target_manager

	if command:
		if command in __main__.__dict__:
			__main__.__dict__[command] ()
		else:
			sys.stderr.write ('no such command: ' + command)
			sys.exit (2)

if __name__ == '__main__':
	main ()
