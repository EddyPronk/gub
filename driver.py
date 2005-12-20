#!/usr/bin/python

import __main__
import optparse
import os
import re
import string
import sys

sys.path.insert (0, 'specs/')

import buildnumber
import framework
import gub
import settings as settings_mod
import xpm

def build_package (settings, manager, package):
	for d in package.dependencies:
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

				if not settings.keep_build:
					package.clean ()

			if stage != 'clean':
				package.set_done (stage, stages.index (stage))


def get_settings (platform):
	init  = {
		'darwin': 'powerpc-apple-darwin7',
		'mingw': 'i686-mingw32',
		'linux': 'linux'
		}[platform]
	
	settings = settings_mod.Settings (init)
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

Commands:

download         - download packages
build-tool       - build cross compiler/linker
manage-tool      - package manager for cross compilers/linkers
build-target     - build target packages
manage-target    - package manager for target dir
build-installer  - build installer for platform
    
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
	p.add_option ('-k', '--keep', action='store_true',
		      dest="keep_build",
		      default=None,
		      help='leave build and src dir for inspection')
	return p

def run_package_manager (m, commands):
	c = commands.pop (0)
	args = commands
	if args and args[0]== 'all':
		args = m._packages.keys()
		
	if c == 'install':
		for p in args:
			if m.name_is_installed (p):
				print '%s already installed' % p

		for p in args:
			if not m.name_is_installed (p):
				m.name_install (p)
				
	elif c in ('uninstall', 'remove'):
		for p in args:
			if not m.name_is_installed (p):
				raise '%s not installed' % p
			
		for p in args:
			m.name_uninstall (p)

	elif c == 'query':
		print '\n'.join ([p.name() for p in  m.installed_packages ()])
		
	elif c == 'query-known':
		print '\n'.join (m._packages.keys ())
		
	elif c == 'list-files':
		for p in args:
			if not m.name_is_installed (p):
				print '%s not installed' % p
			else:
				print m.name_files (p)
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
	for p in install_pkg_manager._packages.values ():
		install_pkg_manager.install_package (p)
		
	for p in framework.get_installers (settings):
		print 'installer: ' + p.name()
		gub.log_command (' *** Stage: %s (%s)\n' % ('create', p.name()))
		p.create ()
		

def run_builder (settings, pkg_manager, args):
	ps = pkg_manager._packages.values ()

	pkgs = [] 
	if args and args[0] == 'all':
		pkgs = pkg_manager._packages.values()
	else:
		pkgs = [pkg_manager._packages[name] for name in args]

	for p in pkgs:
		build_package (settings, pkg_manager, p)


def download_sources (manager):
	for p in manager._packages.values(): 
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
	settings.keep_build = options.keep_build
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
	
	for m in tool_manager, target_manager:
		m.resolve_dependencies ()
		for p in m._packages.values():
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
		for p in target_manager._packages.values ():
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
