#!/usr/bin/python

import __main__
import optparse
import os
import re
import string
import sys

sys.path.insert (0, 'specs/')

import gub
import framework

def grok_sh_variables (self, file):
	dict = {}
	for i in open (file).readlines ():
		m = re.search ('^(\w+)\s*=\s*(\w*)', i)
		if m:
			k = m.group (1)
			s = m.group (2)
			dict[k] = s

	return dict

class Settings:
	def __init__ (self, arch):
		self.target_gcc_flags = '' 
		self.topdir = os.getcwd ()
		self.downloaddir = os.getcwd () + '/downloads'
		self.build_architecture = gub.read_pipe ('gcc -dumpmachine')[:-1]
		self.srcdir = os.path.join (self.topdir, 'src')
		self.specdir = self.topdir + '/specs'
		self.nsisdir = self.topdir + '/nsis'
		self.gtk_version = '2.8'

		self.target_architecture = arch
		self.tool_prefix = arch + '-'
		self.targetdir = self.topdir + '/target/%s' % self.target_architecture
		self.builddir = self.targetdir + '/build'
		self.garbagedir = self.targetdir + '/garbage'
		self.statusdir = self.targetdir + '/status'
		self.gub_uploads = self.targetdir + '/uploads/gub'
		# FIXME: rename to target_root?
		self.system_root = self.targetdir + '/system'
		self.installdir = self.targetdir + '/install'
		self.tooldir = self.targetdir + '/tools'

		# INSTALLERS
		self.gubinstall_root = self.targetdir + '/installer'
		self.installer_uploads = self.targetdir + '/uploads'
		self.bundle_version = None
		self.package_arch = re.sub ('-.*', '', self.build_architecture)
		self.build = '1'

	def get_substitution_dict (self):
		d = {}
		for (k,v) in self.__dict__.items ():
			if type (v) <> type (''):
				continue

			d[k] = v

		d.update({
			'sourcesdir': self.srcdir,
			'build_autopackage': self.builddir + '/autopackage',
			})
		
		return d
			
	def create_dirs (self): 
		for a in (
			'downloaddir',
			'garbagedir',
			'gub_uploads',
			'installer_uploads',
			'specdir',
			'srcdir',
			'statusdir',
			'system_root',
			'targetdir',
			'topdir',
			):
			dir = self.__dict__[a]
			if os.path.isdir (dir):
				continue

			gub.system ('mkdir -p %s' % dir)

def process_package (package):
	package.download ()

	for stage in ('untar', 'patch', 'configure', 'compile', 'install',
		      'package', 'sysinstall'):
        	if not package.is_done (stage):
			print >> sys.stderr, 'gub:' + package.name () + ':' + stage
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


def build_packages (settings, packages):
	for i in packages:
		process_package (i)

def strip_gubinstall_root (root):
	"Remove unnecessary cruft."
	
	for i in (
		'bin/*-config',
		'bin/*gettext*',
		'bin/[cd]jpeg',
		'bin/msg*',
		'bin/xmlwf',
		'doc'
		'include',
		'info',
		'include',
		'lib/pkgconfig',
		'man',
		'share/doc',
		'share/gettext/intl',
		'share/ghostscript/8.15/Resource/',
		'share/ghostscript/8.15/doc/',
		'share/ghostscript/8.15/examples',
		'share/gs/8.15/Resource/',
		'share/gs/8.15/doc/',
		'share/gs/8.15/examples',
		'share/gtk-doc',
		'share/info',
		'share/man',
		'share/omf',
		):
		
		os.system ('cd %(root)s && rm -rf %(i)s' % locals ())
	os.system ('cd %(root)s && rm -f lib/*.a' % locals ())
## FIXME: c/p from buildmac.py
##	gub.system ('cd %(root)s && strip bin/*' % locals ())
##	gub.system ('cd %(root)s && cp etc/pango/pango.modules etc/pango/pango.modules.in ' % locals ())

def make_installers (settings, packages):
	# FIXME: todo separate lilypond-framework, lilypond packages?
	gub.system ('rm -rf %(gubinstall_root)s' % settings.__dict__)
	for i in packages:
		print >> sys.stderr, 'gub:' + i.name () + ':' + 'install_gub'
		i.install_gub ()
		strip_gubinstall_root (i.gubinstall_root () % i.package_dict ())
	for i in framework.get_installers (settings):
		print >> sys.stderr, 'gub:' + i.name () + ':' + 'create'
		i.create ()

def get_settings (platform):
	if platform == 'darwin':
		settings = Settings ('powerpc-apple-darwin7')
		settings.target_gcc_flags = '-D__ppc__'
	elif platform == 'mingw':
		settings = Settings ('i586-mingw32msvc')
		settings.target_gcc_flags = '-mwindows -mms-bitfields'
		settings.platform = 'mingw'
	elif platform == 'mingw-fedora':
		settings = Settings ('i386-mingw32')
		settings.target_gcc_flags = '-mwindows -mms-bitfields'
		settings.platform = 'mingw'
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
		settings.package_arch = 'i386'
		os.environ['CC'] = settings.gcc
		os.environ['CXX'] = settings.gxx
		# FIXME: some libraries, gettext eg, do not build with
		# gcc-4.0.
		os.environ['APBUILD_CC'] = 'gcc-3.4'
		# FIXME: CXX1 for < 3.4 abi, CXX2 for >= 3.4 abi
		# but APBUILD_CXX2 apg++ --version yields 4.0.3 :-(
		os.environ['APBUILD_CXX1'] = 'g++-3.4'
		os.environ['LD'] = settings.ld
	else:
		raise 'unknown platform', platform 
		
	return settings

def do_options ():
	p = optparse.OptionParser (usage = "driver.py [options] platform",
				   description = "Grand Unified Builder. Specify --package-version to set build version")
	p.add_option ('-V', '--verbose', action = 'store_true', 
		      dest = "verbose")
	p.add_option ('', '--package-version', action = 'store',
		      dest = "version")
	p.add_option ('-p', '--platform', action = 'store',
		      dest = "platform",
		      type = 'choice',
		      default = None,
		      help = 'select platform',
		      choices = ['linux', 'darwin', 'mingw', 'mingw-fedora'])

	(opts, commands)  = p.parse_args ()
	if not opts.platform:
		p.print_help()
		sys.exit (2)
	return opts

def main ():
	options = do_options ()
	settings = get_settings (options.platform)
	
	gub.start_log ()
	settings.verbose = options.verbose

	#FIXME: used, but not not set anywhere; what's the idea?
	#settings.bundle_version = None
	settings.bundle_version = 'noel'
	
	settings.create_dirs ()

	os.environ["PATH"] = '%s/%s:%s' % (settings.tooldir, 'bin',
                                           os.environ["PATH"])

	packages = []
	if options.platform == 'darwin':
		import darwintools
		packages += darwintools.get_packages (settings)
	if options.platform.startswith ('mingw'):
		import mingw
		packages += mingw.get_packages (settings)

	packages += framework.get_packages (settings)

	build_packages (settings, packages)
	make_installers (settings, packages)

if __name__ == '__main__':
	main ()
