#!/usr/bin/python

'''
  gup-manager - Keep GUB root up to date
  
  License: GNU GPL
'''

import __main__
import os
import re
import string
import sys

sys.path.insert (0, 'lib/')

import gub
import settings as settings_mod
import gup2

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
		self.rc_file = '.gup-manager.rc'
		self.name_p = 0
		self.nodeps_p = 0
		self.command = 'help'
		self.packagename = 0
		self.read_gup_rc ()
		self.get_options ()

	def get_options (self):
		import getopt
		(options, arguments) = getopt.getopt (sys.argv[1:],
							   'B:hm:np:r:xv',
							   (
			'branch=',
			'help',
			'mirror=',
			'name',
			'platform=',
			'no-deps',
			'root=',
			'verbose',
			))

		if len (arguments) > 0:
			self.command = re.sub ('-', '_', arguments.pop (0))
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
			elif o == '--platform' or o == '-p':
				self.platform = a
				self.ROOT = ''
			elif o == '--name' or o == '-n':
				self.name_p = 1
			elif o == '--no-deps' or o == '-x':
				self.nodeps_p = 1
			elif o == '--verbose' or o == '-v':
				self.verbose = 1
			else:
				sys.stderr.write ('no such option: ' + o)
				sys.stderr.write ('\n\n')
				usage (self)
				sys.exit (2)
			# parse all options to get better help
			if self.command == 'help':
				usage (self)
				sys.exit (0)

	def read_gup_rc (self):
		if os.path.exists (self.rc_file):
			print 'reading', self.rc_file
			h = open (self.rc_file)
			for i in h.readlines ():
				k, v = i.split ('=', 2)
				if k in self.rc_options:
					self.__dict__[k] = eval (v)

	def write_gup_rc (self):
		"Write defaults. "
		
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
		'''write .gup-apt.rc'''
		self.options.write_gup_rc ()
		
	def available (self):
		print '\n'.join (self.pm._packages.keys ())

	def files (self):
		'''list installed files'''
		for p in self.options.arguments:
			if not self.pm.is_installed (p):
				print '%s not installed' % p
			else:
				print '\n'.join (self.pm.installed_files (p))

	def find (self):
		'''package containing file'''
		regexp = re.sub ('^%s/' % self.options.ROOT, '/',
				 self.options.packagename)
		regexp = re.compile (regexp)
		hits = []
		for p in sort (self.pm.installed_packages ()):
			hits += ['%s: /%s' % (p, i)
				 for i in self.pm.installed_files (p)
				 if regexp.search ('/%s' % i)]
		print (string.join (hits, '\n'))

	def help (self):
		'''help COMMAND'''
		if len (self.options.arguments) < 1:
			usage (self.options)
			sys.exit ()

		print  Command.__dict__[self.options.packagename].__doc__

	def install (self):
		'''download and install packages with dependencies'''
		packs=[]
		for p in self.options.arguments:
			if self.pm.is_installed (p):
				print '%s already installed' % p
			else:
				packs.append (p)

		packs = gup2.topologically_sorted (packs, {}, self.pm.dependencies)
		for p in packs:
			self.pm.install_package (p)

	def list (self):
		'''installed packages'''
		if self.options.name_p:
			print '\n'.join (sort (self.pm.installed_packages ()))
		else:
			print '\n'.join (sort (['%(name)-20s%(version)s' % d for d in self.pm.installed_package_dicts()]))

	def remove_package (self, p, packs):
		if not self.pm.is_installed (p):
			print '%s not installed' % p
		else:
			self.pm.uninstall_package (p)
		
	def remove (self):
		'''uninstall packages'''

		packages = gup2.topologically_sorted (self.options.arguments, {},
						      self.pm.dependencies,
						      recurse_stop_predicate
						      =lambda p: p not in self.options.arguments)
		packages.reverse ()
		for p in packages:
			self.remove_package (p, packages) 

def usage (options):
	sys.stdout.write ('''%s [OPTION]... COMMAND [PACKAGE]...

Commands:
''' % os.path.basename (sys.argv[0]))
	d = Command.__dict__
	commands = filter (lambda x:
			   type (d[x]) == type (usage) and d[x].__doc__, d)
	sys.stdout.writelines (map (lambda x:
				    "    %s - %s\n"
				    % (re.sub ('_', '-', x), d[x].__doc__),
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
    -x,--no-deps           ignore dependencies

''' % d)
	if os.path.exists (d['rc_file']):
		sys.stdout.write (r'''
Defaults are taken from ./%(rc_file)s
''' %d)

def main ():
	options = Options ()
	if not options.platform:
		sys.stderr.write ('need platform setting, use -p option')
		sys.stderr.write ('\n\n')
		usage (options)
		sys.exit (2)
		
	settings = settings_mod.Settings (options.platform)
	settings.options = options
	settings.lilypond_branch = options.BRANCH

	if not options.ROOT:
		options.ROOT = ('target/%(platform)s/system'
				% settings.__dict__)

	target_manager = gup2.Dependency_manager (options.ROOT, settings.os_interface)
	if options.command == 'install':
		target_manager.read_package_headers (settings.expand ('%(gub_uploads)s/'))
	
	if options.command:
		commands = Command (target_manager, options)
		if options.command in Command.__dict__:
			Command.__dict__[options.command] (commands)
		else:
			sys.stderr.write ('no such command: ' + options.command)
			sys.stderr.write ('\n')
			sys.exit (2)

if __name__ == '__main__':
	main ()
