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
	settings.os_interface.log_command (package.expand (' ** Package: %(name)s (%(version)s, %(build)s)\n'))

	for d in package.dependencies:
		if not manager.is_installed (d):
			settings.os_interface.log_command ('building dependency: ' + d.name ()
							   + ' for package: ' + package.name ()
							   + '\n')
			build_package (settings, manager, d)
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
		## FIXME: assuming linux is native...
		settings.target_architecture = settings.build_architecture
	elif platform == 'freebsd':
		pass
	else:
		raise 'unknown platform', platform 

	return settings

def add_options (settings, options):
	for o in options.settings:
		(key, val) = tuple (o.split ('='))
		settings.__dict__[key] = val

	settings.options = options
	settings.bundle_version = options.package_version
	settings.bundle_build = options.package_build
	settings.use_tools = options.use_tools
	settings.create_dirs ()
	
	if settings.platform == 'linux':
		settings.tool_prefix = ''

	if settings.platform == 'linux' or settings.platform == 'freebsd':

		# Use apgcc to avoid using too new GLIBC symbols
		# possibly gcc/g++ -Wl,--as-needed, ld --as-needed has
		# same effect?

		# FIXME: this does not work while building the compiler
		if not options.use_tools:
			settings.gcc = 'apgcc'
			settings.gxx = 'apg++'
			settings.ld = settings.tool_prefix + 'ld --as-needed'
			os.environ['CC'] = settings.gcc
			os.environ['CXX'] = settings.gxx
			os.environ['LD'] = settings.ld
			os.environ['APBUILD_CC'] = settings.tool_prefix + 'gcc'
			os.environ['APBUILD_CXX1'] = settings.tool_prefix + 'g++'
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
	p = optparse.OptionParser (usage="""driver.py [OPTION]... COMMAND [PACKAGE]...

Commands:

download          - download packages
build             - build target packages
build-installer   - build installer root
package-installer - build installer binary

""",
				   description="Grand Unified Builder.  Specify --package-version to set build version")
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
		      choices=['darwin', 'freebsd', 'linux', 'mingw'])
	p.add_option ('-s', '--setting', action='append',
		      dest="settings",
		      type='string',
		      default=[],
		      help='add a variable')
	p.add_option ('-k', '--keep', action='store_true',
		      dest="keep_build",
		      default=None,
		      help='leave build and src dir for inspection')
	p.add_option ('', '--stage', action='store',
		      dest='stage', default=None,
		      help='Force rebuild of stage') 
	p.add_option ('-t', '--tools', action='store_true',
		      dest='use_tools', default=None,
		      help='use tool package manager') 
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
	os.environ["PATH"] = '%s/%s:%s' % (settings.tooldir, 'bin',
                                           os.environ["PATH"])

	
	pkgs = [] 
	if args and args[0] == 'all':
		pkgs = pkg_manager._packages.values()
	else:
		pkgs = [pkg_manager._packages[name] for name in args]

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
	tool_manager, target_manager = xpm.get_managers (settings)

	c = commands.pop (0)
	if c == 'download':
		download_sources (tool_manager)
		download_sources (target_manager)
	elif c == 'build':
		pm = xpm.determine_manager (settings,
					    [tool_manager, target_manager],
					    commands)
		run_builder (settings, pm, commands)
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
