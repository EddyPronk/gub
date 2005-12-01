#!/usr/bin/python

import __main__
import getopt
import os
import re
import string
import sys

sys.path.insert (0, 'specs/')

import gub
import framework


class Settings:
	def __init__ (self, arch):
		self.target_gcc_flags = '' 
		self.topdir = os.getcwd ()
		self.downloaddir = os.getcwd () + '/downloads'
		self.build_architecture = gub.read_pipe ('gcc -dumpmachine')[:-1]
		self.srcdir = os.path.join (self.topdir, 'src')
		self.specdir = self.topdir + '/specs'
		self.gtk_version = '2.8'

		self.target_architecture = arch
		self.tool_prefix = arch + '-'
		self.targetdir = self.topdir + '/target/%s' % self.target_architecture
		self.builddir = self.targetdir + '/build'
		self.garbagedir = self.targetdir + '/garbage'
		self.statusdir = self.targetdir + '/status'
		# FIXME: rename to gubpackagedir ?
		self.uploaddir = self.targetdir + '/uploads'
		# FIXME: rename to target_root?
		self.system_root = self.targetdir + '/system'
		self.installdir = self.targetdir + '/install'
		self.tooldir = self.targetdir + '/tools'

	def create_dirs (self): 
		for a in ('downloaddir',
			  'garbagedir',
			  'specdir', 'srcdir', 'statusdir', 'system_root',
                          'targetdir', 'topdir',
			  'uploaddir'):
			dir = self.__dict__[a]
			if os.path.isdir (dir):
				continue

			gub.system ('mkdir -p %s' % dir)

def process_package (package):
	package.download ()

	for stage in ('untar', 'patch', 'configure', 'compile', 'install',
		      'package', 'sysinstall'):
        	if not package.is_done (stage):
			print 'gub:' + package.name () + ':' + stage
                	if stage == 'untar':
                        	package.untar ()
			elif stage == 'patch':
                        	package.patch ()
			elif stage == 'configure':
                        	package.configure ()
			elif stage == 'compile':
                        	package.compile ()
			elif stage == 'install':
                        	package.install ()
			elif stage == 'package':
                        	package.package ()
			elif stage == 'sysinstall':
                        	package.sysinstall ()
			package.set_done (stage)


def process_packages (packages):
	for i in packages:
		process_package (i)
		
def main ():
	(options, files) = getopt.getopt (sys.argv[1:], 'V', ['verbose'])
	verbose = 0 
	for (o, a) in options:
		if o == '--verbose' or o == '-V':
			verbose = 1

	try:
		platform = files[0]
	except IndexError:
		platform = ''

	platforms = ('linux', 'mac', 'mingw', 'mingw-fedora')
	if platform not in platforms:
		print 'unsupported platform:', platform
		print 'use:', string.join (platforms)
		sys.exit (1)

	if platform == 'mac':
		settings = Settings ('powerpc-apple-darwin7')
	elif platform == 'mingw':
		settings = Settings ('i586-mingw32msvc')
		settings.target_gcc_flags = '-mwindows -mms-bitfields'
	elif platform == 'mingw-fedora':
		settings = Settings ('i386-mingw32')
		settings.target_gcc_flags = '-mwindows -mms-bitfields'
		platform = 'mingw'
	elif platform == 'linux':
		settings = Settings ('linux')
		platform = 'linux'
		settings.target_architecture = settings.build_architecture
		# Use apgcc to avoid using too new GLIBC symbols
		# possibly gcc/g++ -Wl,--as-needed, ld --as-needed has
		# same effect?
		settings.gcc = 'apgcc'
		settings.gxx = 'apg++'
		settings.ld = 'ld --as-needed'
		settings.tool_prefix = ''
		os.environ['CC'] = settings.gcc
		os.environ['CXX'] = settings.gxx
		# FIXME: some libraries, gettext eg, do not build with
		# gcc-4.0.
		os.environ['APBUILD_CC'] = 'gcc-3.4'
		# CXX1 for < 3.4 abi, CXX2 for >= 3.4 abi
		os.environ['APBUILD_CXX2'] = 'g++-3.4'
		os.environ['LD'] = settings.ld

	gub.start_log ()
	settings.verbose = verbose
	settings.platform = platform
	
	settings.create_dirs ()

	os.environ["PATH"] = '%s/%s:%s' % (settings.tooldir, 'bin',
                                           os.environ["PATH"])

	if platform == 'mac':
		import darwintools
		process_packages (darwintools.get_packages (settings))
	if platform.startswith ('mingw'):
		import mingw
		process_packages (mingw.get_packages (settings))

	process_packages (framework.get_packages (settings, platform))


if __name__ == '__main__':
    	main ()
