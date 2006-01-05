#!/usr/bin/python

import __main__
import optparse
import os
import re
import string
import sys
import inspect
import types

sys.path.insert (0, 'specs/')

import buildnumber
import framework
import gub
import settings as settings_mod
import xpm

def build_package (settings, manager, package):
	if manager.is_installed (package):
		return
	
	settings.os_interface.log_command (package.expand (' ** Package: %(name)s (%(version)s, %(build)s)\n'))

	deps = package.build_dependencies + package.dependencies
	for d in deps:
		settings.os_interface.log_command ('building dependency: ' + d.name ()
						   + ' for package: ' + package.name ()
						   + '\n')
		build_package (settings, manager, d)
		if not manager.is_installed (d):
			manager.install_package (d)

	stages = ['untar', 'patch', 'configure', 'compile', 'install',
		  'package', 'clean']
	
	available = dict (inspect.getmembers (package, callable))

	forced_idx = 100

	if settings.options.stage:
		(available[settings.options.stage]) ()
		return

	if manager.is_installable (package):
		return
	
	for stage in stages:
		if not available.has_key (stage):
			continue
		
		idx = stages.index (stage)
        	if not package.is_done (stage, idx):

			# ugh.
			package.os_interface.log_command (' *** Stage: %s (%s)\n' % (stage, package.name ()))

			if stage == 'clean' and  settings.options.keep_build:
				os.unlink (package.stamp_file ())
				continue

			(available[stage]) ()

			if stage != 'clean':
				package.set_done (stage, stages.index (stage))

def get_settings (platform):
	settings = settings_mod.Settings (platform)
	settings.build_number_db = buildnumber.Build_number_db (settings.topdir)
	
	if platform == 'darwin':
		settings.target_gcc_flags = '-D__ppc__'
	elif platform == 'mingw':
		settings.target_gcc_flags = '-mwindows -mms-bitfields'
	elif platform == 'linux':
		pass
	elif platform == 'freebsd':
		pass
	elif platform == 'local':
		pass
	else:
		raise 'unknown platform', platform 

	return settings

def add_options (settings, options):
	for o in options.settings:
		(key, val) = tuple (o.split ('='))
		key = re.sub ('[^a-z0-9_A-Z]','_', key)
		settings.__dict__[key] = val

	settings.options = options
	settings.lilypond_branch = options.lilypond_branch
	settings.bundle_version = options.installer_version
	settings.bundle_build = options.installer_build
	settings.use_tools = options.use_tools
	settings.create_dirs ()
	
	if settings.platform == 'linux':
		settings.tool_prefix = ''

	if settings.platform == 'linux' or settings.platform == 'freebsd':

		# FIXME: this for deb/rpm/slackware package archs
		settings.package_arch = 'i386'

		settings.framework_version = '0.0.0'
		# FIXME: must not use lilypond version (ie bundle version)
		# in framework dir.  Framework should be more or less
		# constant/stable.
		#settings.framework_dir = ('lib/lilypond/%(bundle_version)s/lib'
		settings.framework_dir = ('lib/lilypond/framework/%(framework_version)s'
					   % settings.__dict__)
		settings.framework_root = ('%(installer_root)s/usr/%(framework_dir)s'
					   % settings.__dict__)
		# This works, but better avoid depending on autopackage.
		# os.environ['APBUILD_PROJECTNAME'] = 'lilypond/framework/0.0.0/usr/lib'

def get_cli_parser ():
	p = optparse.OptionParser ()

# WTF, how to get help option to show in right order?
#	p.add_option ('-h', '--help',
#		      help='print this help')
	p.usage="""driver.py [OPTION]... COMMAND [PACKAGE]...

Commands:

download          - download packages
build             - build target packages
build-installer   - build installer root
package-installer - build installer binary

"""
	p.description="Grand Unified Builder.  Specify --package-version to set build version"

	p.add_option ('-B', '--branch', action='store',
		      dest="lilypond_branch",
		      type='choice',
		      default='HEAD',
		      help='select lilypond branch [HEAD]',
		      choices=['lilypond_2_6', 'HEAD'])
	p.add_option ('-b', '--build-platform', action='store',
		      dest="build_platform",
		      type='choice',
		      default='linux',
		      help='select build platform [linux]',
		      choices=['darwin', 'linux'])
	p.add_option ('', '--installer-version', action='store',
		      default="0.0.0",
		      dest="installer_version")
	p.add_option ('', '--installer-build', action='store',
		      default="0",
		      dest="installer_build")
	p.add_option ('-k', '--keep', action='store_true',
		      dest="keep_build",
		      default=None,
		      help='leave build and src dir for inspection')
	p.add_option ('-p', '--target-platform', action='store',
		      dest="platform",
		      type='choice',
		      default=None,
		      help='select target platform',
		      choices=['local', 'darwin', 'freebsd', 'linux', 'mingw'])
	p.add_option ('-s', '--setting', action='append',
		      dest="settings",
		      type='string',
		      default=[],
		      help='add a variable')
	p.add_option ('', '--stage', action='store',
		      dest='stage', default=None,
		      help='Force rebuild of stage') 
	p.add_option ('-t', '--tools', action='store_true',
		      dest='use_tools', default=None,
		      help='use tool package manager') 
	p.add_option ('-V', '--verbose', action='store_true', 
		      dest="verbose")
	return p

def build_installers (settings, target_manager):
	os.system ('rm -rf %s' %  settings.installer_root)
	install_manager = xpm.Package_manager (settings.installer_root,
					       settings.os_interface)

	framework_manager = None
	if (settings.platform.startswith ('linux')
	    or settings.platform.startswith ('freebsd')):
		# Hmm, better to configure --prefix=framework_root --xxxfix=fr?
		# and install everything in / ?
		framework_manager = xpm.Package_manager (settings.framework_root,
							 settings.os_interface)

	for p in target_manager._packages.values ():
		if isinstance (p, gub.Sdk_package):
			continue
		if (p.name () != 'lilypond'
		    and framework_manager):
			framework_manager.register_package (p)
		else:
			install_manager.register_package (p)

	for p in install_manager._packages.values ():
		install_manager.install_package  (p)
	if framework_manager:
		for p in framework_manager._packages.values ():
			framework_manager.install_package  (p)

def package_installers (settings):
	import installer
	for p in installer.get_installers (settings):
		settings.os_interface.log_command (' *** Stage: %s (%s)\n'
						   % ('create', p.name ()))
		p.create ()
		
def run_builder (settings, pkg_manager, args):
	PATH = os.environ["PATH"]

	## crossprefix is also necessary for building cross packages, such as GCC 
	os.environ["PATH"] = settings.expand ('%(crossprefix)s/bin:%(PATH)s', locals())
	pkgs = [] 
	if args and args[0] == 'all':
		pkgs = pkg_manager._packages.values()
	else:
		pkgs = [pkg_manager._packages[name] for name in args]

	for p in pkgs:
		if pkg_manager.is_installed (p):
			pkg_manager.uninstall_package (p)
		
	for p in pkgs:
		build_package (settings, pkg_manager, p)

def download_sources (manager):
	for p in manager._packages.values():
		p.os_interface.log_command ("Considering %s\n" % p.name())
		p.do_download ()

def main ():
	cli_parser = get_cli_parser ()
	(options, commands)  = cli_parser.parse_args ()

	if not options.platform:
		raise 'error: no platform specified'
		cli_parser.print_help ()
		sys.exit (2)
	
	settings = get_settings (options.platform)
	add_options (settings, options)
	target_manager = xpm.get_manager (settings)


	## crossprefix is also necessary for building cross packages, such as GCC 

	PATH = os.environ["PATH"]
	os.environ["PATH"] = settings.expand ('%(tooldir)s/bin:%(PATH)s', locals())


	c = commands.pop (0)
	if c == 'download':
		download_sources (target_manager)
	elif c == 'build':
		run_builder (settings, target_manager, commands)
	elif c == 'build-installer':
		build_installers (settings, target_manager)
	elif c == 'package-installer':
		package_installers (settings)
	else:
		raise 'unknown driver command %s.' % c
		cli_parser.print_help ()
		sys.exit (2)
			
if __name__ == '__main__':
	main ()
