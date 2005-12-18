#!/usr/bin/python

import __main__
import optparse
import os
import re
import string
import sys

sys.path.insert (0, 'specs/')

import xpm
import gub
import framework
import buildnumber



class Settings:
	def __init__ (self, arch):
		self.target_gcc_flags = '' 
		self.topdir = os.getcwd ()
		self.downloaddir = self.topdir + '/downloads'
		self.patchdir = self.topdir + '/patches'
		self.build_architecture = gub.read_pipe ('gcc -dumpmachine')[:-1]
		self.specdir = self.topdir + '/specs'
		self.nsisdir = self.topdir + '/nsis'
		self.gtk_version = '2.8'

		self.target_architecture = arch
		self.tool_prefix = arch + '-'
		self.targetdir = self.topdir + '/target/%s' % self.target_architecture

		## Patches are architecture dependent, 
		## so to ensure reproducibility, we unpack for each
		## architecture separately.
		self.allsrcdir = os.path.join (self.targetdir, 'src')
		
		self.builddir = self.targetdir + '/build'
		self.statusdir = self.targetdir + '/status'

		## Safe uploads, so that we can rm -rf target/*
		## and still cheaply construct a (partly) system root
		## from .gub packages.
		## self.gub_uploads = self.targetdir + '/uploads/gub'
		self.uploads = self.topdir + '/uploads'
		self.gub_uploads = self.uploads + '/gub'

		# FIXME: rename to target_root?
		self.system_root = self.targetdir + '/system'
		self.manager_dir = self.system_root + '/etc/setup'
		self.installdir = self.targetdir + '/install'
		self.tooldir = self.targetdir + '/tools'

		# INSTALLERS
		self.installer_root = self.targetdir + '/installer'
		##self.installer_uploads = self.targetdir + '/uploads'
		self.installer_uploads = self.uploads
		self.bundle_version = None
		self.bundle_build = None
		self.package_arch = re.sub ('-.*', '', self.build_architecture)

		self.python_version = '2.4'

	def get_substitution_dict (self):
		d = {}
		for (k,v) in self.__dict__.items ():
			if type (v) <> type (''):
				continue

			d[k] = v

		d.update({
			'build_autopackage': self.builddir + '/autopackage',
			})
		
		return d
			
	def create_dirs (self): 
		for a in (
			'downloaddir',
			'gub_uploads',
			'installer_uploads',
			'specdir',
			'allsrcdir',
			'statusdir',
			'system_root',
			'targetdir',
			'tooldir',
			'topdir',
			):
			dir = self.__dict__[a]
			if os.path.isdir (dir):
				continue

			gub.system ('mkdir -p %s' % dir)

def build_package (settings, manager, package):
	for d in package.depends:
		if not manager.is_installed (d):
			build_package (settings, manager, d)
			manager.install_package (d)

	if manager.is_installable (package):
		return
	
	if manager.is_installed (package):
		manager.uninstall_package (package)
		

	gub.log_command (package.expand_string (' ** Package: %(name)s (%(version)s, %(build)s)\n'))

	stages = ['untar', 'patch', 'configure', 'compile', 'install',
		  'package', 'sysinstall', 'clean']
	for stage in stages:
        	if not package.is_done (stage, stages.index (stage)):
			gub.log_command (' *** Stage: %s (%s)\n' % (stage, package.name ()))

			## UGH. fixme, need parameterize.
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
			elif stage == 'clean':
## advancing the build number should be done during upload.
## consequence: the build number should be kept in a repository on lilypond.org
				package.clean ()

			if stage <> 'clean':
				package.set_done (stage, stages.index (stage))


def get_settings (platform):
	init  = {
		'darwin': 'powerpc-apple-darwin7',
		'mingw': 'i686-mingw32',
		'linux': 'linux'
		}[platform]
	
	settings = Settings (init)
	settings.manager = None
	settings.platform = platform
	
	if platform == 'darwin':
		settings.target_gcc_flags = '-D__ppc__'
	elif platform == 'mingw':
		settings.target_gcc_flags = '-mwindows -mms-bitfields'
	elif platform == 'linux':
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

def get_cli_parser ():
	p = optparse.OptionParser (usage="""driver.py [OPTION]... COMMAND [PACKAGE]...

Try help as command for. 

Example:
    ./driver.py -p mingw download mingw-runtime lilypond
    ./driver.py -p mingw build-target all
    ./driver.py -p mingw manage-tool install all
""",
				   description="Grand Unified Builder.  Specify --package-version to set build version")
        p.add_option ('-o', '--offline', action = 'store_true',
                      default=None,
                      dest='offline')
	p.add_option ('-V', '--verbose', action='store_true', 
		      dest="verbose")
	p.add_option ('', '--package-version', action='store',
		      dest="package_version")
	p.add_option ('', '--package-build', action='store',
		      dest="package_build")
	p.add_option ('-p', '--platform', action='store',
		      dest="platform",
		      type='choice',
		      default=None,
		      help='select platform',
		      choices=['linux', 'darwin', 'mingw', 'xmingw', 'xmingw-fedora'])
	p.add_option ('-s', '--setting', action='append',
		      dest="settings",
		      type='string',
		      default=[],
		      help='add a variable')

	return p

def run_package_manager (m, commands):
	c = commands.pop (0)
	args = commands
	if args and args[0]== 'all':
		args = m.known_packages.keys()
		
	if c == 'install':
		for p in args:
			if m.is_name_installed (p):
				print '%s already installed' % p

		for p in args:
			if not m.is_name_installed (p):
				m.install_named (p)
	elif c in ('uninstall', 'remove'):
		for p in args:
			if not m.is_name_installed (p):
				raise '%s not installed' % p
			
		for p in args:
			m.uninstall_named (p)

	elif c == 'query':
		print '\n'.join ([p.name() for p in  m.installed_packages ()])
		
	elif c == 'query-known':
		print '\n'.join (m.known_packages.keys ())
		
	elif c == 'list-files':
		for p in args:
			if not m.is_name_installed (p):
				print '%s not installed' % p
			else:
				print m.file_list_of_name(p)
	elif c == 'help':
		print '''


install <pkgs> - install listed pkgs including deps.
uninstall <pkgs> - install listed pkgs including deps.
list-files <pkgs> - install listed pkgs including deps.
query - list installed packages
query-known - list known packages
help - this info


<pkgs> may be all "all" for all known packages.

'''
		sys.exit (0)
		
	else:
		raise 'unknown xpm command %s ' % c


def build_installers (settings, install_pkg_manager):
	for p in install_pkg_manager.known_packages.values ():
		install_pkg_manager.install_package (p)
		
	for p in framework.get_installers (settings):
		print 'installer: ' + p.name()
		gub.log_command (' *** Stage: %s (%s)\n' % ('create', p.name()))
		p.create ()
		

def run_builder (settings, pkg_manager, args):
	ps = pkg_manager.known_packages.values ()

	pkgs = [] 
	if args and args[0] == 'all':
		pkgs = pkg_manager.known_packages.values()
	else:
		pkgs = [pkg_manager.known_packages[name] for name in args]

	for p in pkgs:
		build_package (settings, pkg_manager, p)


def download_sources (manager):
	for p in manager.known_packages.values(): 
		p.download ()

def main ():
	cli_parser = get_cli_parser ()
	(options, commands)  = cli_parser.parse_args ()

	if not options.platform:
		cli_parser.print_help()
		sys.exit (2)
	
	settings = get_settings (options.platform)
        settings.offline = options.offline

	for o in options.settings:
		(key, val) = tuple (o.split ('='))
		settings.__dict__[key] = val
		
	gub.start_log (settings)
	settings.verbose = options.verbose
	settings.bundle_version = options.package_version
	settings.bundle_build = options.package_build
	settings.create_dirs ()
	
	target_manager = xpm.Package_manager (settings.system_root)
	tool_manager = xpm.Package_manager (settings.tooldir)

	os.environ["PATH"] = '%s/%s:%s' % (settings.tooldir, 'bin',
                                           os.environ["PATH"])
	
	if options.platform == 'darwin':
		import darwintools
		map (tool_manager.register_package, darwintools.get_packages (settings))
	if options.platform.startswith ('mingw'):
		import mingw
		map (tool_manager.register_package,  mingw.get_packages (settings))

	map (target_manager.register_package, framework.get_packages (settings))

	settings.build_number_db = buildnumber.Build_number_db (settings.topdir)
	tool_manager.resolve_dependencies ()
	target_manager.resolve_dependencies ()

	for p in tool_manager.known_packages.values() + target_manager.known_packages.values():
		settings.build_number_db.set_build_number (p)
	
	c = commands.pop (0)

	if c == 'download':
		download_sources (tool_manager)
		download_sources (target_manager)
	elif c == 'build-tool':
		run_builder (settings, tool_manager, commands)
	elif c == 'build-target':
		run_builder (settings, target_manager, commands)
	elif c == 'manage-tool':
		run_package_manager (tool_manager, commands)
	elif c == 'manage-target':
		run_package_manager (target_manager, commands)
	elif c == 'build-installer':
		gub.system ('rm -rf %s' %  settings.installer_root)
		install_manager = xpm.Package_manager (settings.installer_root)
		for p in target_manager.known_packages.values ():
			if not isinstance (p, gub.Sdk_package):
				install_manager.register_package (p)

		build_installers (settings, install_manager)
		
	elif c == 'help':
		print 'driver commands:  help download {manage,build}-{tool,target} build-installer '
		sys.exit (0)
	else:
		raise 'unknown driver command %s. Try "driver.py help" ' % c
			
if __name__ == '__main__':
	main ()
