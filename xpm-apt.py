#!/usr/bin/python

'''
  xpm - Keep GUB root up to date
  
  License: GNU GPL
'''

import __main__
import os
import re
import string
import sys

sys.path.insert (0, 'specs/')

import framework
import gub
import settings as settings_mod
import xpm

def sort (lst):
	list.sort (lst)
	return lst

class Options:
	def __init__ (self):
		self.platform = ''
		self.BRANCH = 'HEAD'
		self.PLATFORM = ''
		self.ROOT = ''
		self.distname = 'unused'
		self.config = self.ROOT + '/etc/xpm'
		self.mirror = 'file://uploads/gub'
		self.rc_options = ['BRANCH', 'platform', 'PLATFORM', 'ROOT',
				   'mirror', 'distname']
		self.rc_file = '.xpm-apt.rc'
		self.name_p = 0
		self.nodeps_p = 0
		self.tool_p = 0
		self.command = 'help'
		self.packagename = 0
		self.read_xpm_rc ()
		self.get_options ()

	def get_options (self):
		import getopt
		(options, arguments) = getopt.getopt (sys.argv[1:],
							   'B:hm:np:r:tb:x',
							   (
			'branch=',
			'help',
			'mirror=',
			'name',
			'platform=',
			'no-deps',
			'root=',
			'tool'
			))

		if len (arguments) > 0:
			self.command = arguments.pop (0)
		# Hmm, keep arguments as separate list?
		self.arguments = arguments

		if len (arguments) > 0:
			self.packagename = self.arguments[0]
		
		for i in options:
			o = i[0]
			a = i[1]

			if 0:
				pass
			elif o == '--branch' or o == '-B':
				self.BRANCH = a
			elif o == '--help' or o == '-h':
				self.command = 'help'
			elif o == '--mirror' or o == '-m':
				self.mirror = a
			elif o == '--root' or o == '-r':
				self.ROOT = a
			elif o == '--tool' or o == '-t':
				self.tool_p = 1
			elif o == '--platform' or o == '-p':
				self.platform = a
				self.ROOT = ''
			elif o == '--name' or o == '-n':
				self.name_p = 1
			elif o == '--no-deps' or o == '-x':
				self.nodeps_p = 1
			else:
				sys.stderr.write ('no such option: ' + o)
				sys.stderr.write ('\n\n')
				usage (self)
				sys.exit (2)
			# parse all options to get better help
			if self.command == 'help':
				usage (self)
				sys.exit (0)

	def read_xpm_rc (self):
		if os.path.exists (self.rc_file):
			print 'reading', self.rc_file
			h = open (self.rc_file)
			for i in h.readlines ():
				k, v = i.split ('=', 2)
				if k in self.rc_options:
					self.__dict__[k] = eval (v)

	def write_xpm_rc (self):
		"Write defaults in .xpm-apt.rc. "
		
		h = open (self.rc_file, 'w')
		print 'writing', self.rc_file
		for i in self.rc_options:
			h.write ('%s="%s"\n' % (i, self.__dict__[i]))
		h.close ()

class Command:
	def __init__ (self, pm, options):
		self.pm = pm
		self.options = options

	def write_rc (self):
		'''write .xpm-apt.rc'''
		self.options.write_xpm_rc ()
		
	def available (self):
		print '\n'.join (self.pm._packages.keys ())

	def files (self):
		'''list installed files'''
		for p in self.options.arguments:
			if not self.pm.name_is_installed (p):
				print '%s not installed' % p
			else:
				print '\n'.join (self.pm.name_files (p))

	def find (self):
		'''package containing file'''
		regexp = re.sub ('^%s/' % self.options.ROOT, '/',
				 self.options.packagename)
		hits = []
		for self.options.packagename in sort (map (gub.Package.name,
							    self.pm.installed_packages ())):
			for i in self.pm.name_files (self.options.packagename):
				if re.search (regexp, '/%s' % i):
					hits.append ('%s: /%s' % (self.options.packagename, i))
		print (string.join (hits, '\n'))

	def help (self):
		'''help COMMAND'''
		if len (self.options.arguments) < 1:
			usage (self.options)
			sys.exit ()

		print  Command.__dict__[self.options.packagename].__doc__

	def install (self):
		'''download and install packages with dependencies'''
		for p in self.options.arguments:
			if self.pm.name_is_installed (p):
				print '%s already installed' % p

		for p in self.options.arguments:
			if not self.pm.name_is_installed (p):
				if self.options.nodeps_p:
					self.pm.install_single_package (self.pm._packages[p])
				else:
					self.pm.install_package (self.pm._packages[p])

	def list (self):
		'''installed packages'''
		if self.options.name_p:
			print '\n'.join (sort (map (gub.Package.name,
						     self.pm.installed_packages ())))
		else:
			print '\n'.join (sort (map (lambda x: '%-20s%s' % (x.name (),
								     x.full_version ()),
						     self.pm.installed_packages ())))

	def remove (self):
		'''uninstall packages'''
		for p in self.options.arguments:
			if not self.pm.name_is_installed (p):
				raise '%s not installed' % p

		for p in self.options.arguments:
			self.pm.name_uninstall (p)

def usage (options):
	sys.stdout.write ('''%s [OPTION]... COMMAND [PACKAGE]...

Commands:
''' % os.path.basename (sys.argv[0]))
	d = Command.__dict__
	commands = filter (lambda x:
			   type (d[x]) == type (usage) and d[x].__doc__, d)
	sys.stdout.writelines (map (lambda x:
				    "    %s - %s\n" % (x, d[x].__doc__),
			       sort (commands)))
	d = options.__dict__
	sys.stdout.write (r'''
Options:
    -B,--lilypond-branch   select lilypond branch [%(BRANCH)s]
    -h,--help              show brief usage
    -m,--mirror=URL        use mirror [%(mirror)s]
    -n,--name              print package name only
    -p,--platform=NAME     set platform [%(platform)s]
    -r,--root=DIR          set %(PLATFORM)s root [%(ROOT)s]
    -t,--tools             manage tools
    -x,--no-deps           ignore dependencies

Defaults are taken from ./%(rc_file)s
    
''' % d)

def main ():
	options = Options ()
	if not options.platform:
		sys.stderr.write ('need platform setting, use -p option')
		sys.stderr.write ('\n\n')
		usage (options)
		sys.exit (2)
		
	settings = settings_mod.Settings (options.platform)
	settings.lilypond_branch = options.BRANCH

	if not options.ROOT:
		options.ROOT = ('target/%(target_architecture)s/system'
				% settings.__dict__)

	if 1:
		#URG
		import buildnumber
		settings.build_number_db = buildnumber.Build_number_db (settings.topdir)
		settings.framework_dir = 'FUBAR'


	tool_manager, target_manager = xpm.get_managers (settings)

	settings.use_tools = options.tool_p
	pm = xpm.determine_manager (settings,
				    [tool_manager, target_manager],
				    options.arguments)

	pm.resolve_dependencies ()

	if options.arguments and options.arguments[0] == 'all':
		options.arguments = pm._packages.keys ()
		
	if options.command:
		commands = Command (pm, options)
		if options.command in Command.__dict__:
			Command.__dict__[options.command] (commands)
		else:
			sys.stderr.write ('no such command: ' + options.command)
			sys.stderr.write ('\n')
			sys.exit (2)

if __name__ == '__main__':
	main ()
