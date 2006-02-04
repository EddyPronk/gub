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

import framework
import gub
import settings as settings_mod
import xpm

def get_settings (platform):
	settings = settings_mod.Settings (platform)

	if platform not in settings_mod.platforms.keys ():
		raise 'unknown platform', platform
		
	if platform == 'darwin':
		settings.target_gcc_flags = '-D__ppc__'
	elif platform == 'mingw':
		settings.target_gcc_flags = '-mwindows -mms-bitfields'

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
	settings.create_dirs ()

def get_cli_parser ():
	p = optparse.OptionParser ()

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
		      choices=settings_mod.platforms.keys ())
	p.add_option ('-s', '--setting', action='append',
		      dest="settings",
		      type='string',
		      default=[],
		      help='add a variable')
	p.add_option ('', '--stage', action='store',
		      dest='stage', default=None,
		      help='Force rebuild of stage')
	p.add_option ('-V', '--verbose', action='store_true',
		      dest="verbose")
	p.add_option ('', '--force-package', action='store_true',
		      default=False,
		      dest="force_package",
		      help="allow packaging of tainted compiles" )
	return p

def build_installer (settings, target_manager, args):
	os.system ('rm -rf %s' %  settings.installer_root)
	install_manager = xpm.Package_manager (settings.installer_root,
					       settings.os_interface)

	install_manager.include_build_deps = False
	if not args:
		if settings.is_distro:
			args = ['lilypond']
		else:
			# FIXME: this does not work for cygwin,
			# debian, and it is a bit silly too.
			# 'lilypond' should pull in everything it
			# needs, by dependencies
			args = target_manager._packages.keys ()
			args.append ('lilypond')

	pkgs = map (lambda x: target_manager._packages[x], args)
	for p in pkgs:
		if not isinstance (p, gub.Sdk_package):
			install_manager.register_package (p)

	for p in install_manager._packages.values ():
		install_manager.install_package  (p)

def package_installers (settings):
	import installer
	for p in installer.get_installers (settings):
		settings.os_interface.log_command (' *** Stage: %s (%s)\n'
						   % ('create', p.name ()))
		p.create ()

def run_builder (settings, manager, args):
	PATH = os.environ["PATH"]

	## crossprefix is also necessary for building cross packages, such as GCC
	os.environ["PATH"] = settings.expand ('%(crossprefix)s/bin:%(PATH)s',
					      locals ())
	pkgs = map (lambda x: manager._packages[x], args)

	if not settings.options.stage:
		pkgs = manager.topological_sort (pkgs)
		pkgs.reverse ()

		for p in pkgs:
			if (manager.is_installed (p) and
			    not manager.is_installable (p)):
				manager.uninstall_package (p)

	for p in pkgs:
		manager.build_package (p)

def download_sources (manager, args):
	for n in args:
		manager.name_download (n)

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

	## crossprefix is also necessary for building cross packages,
	## such as GCC

	PATH = os.environ["PATH"]
	os.environ["PATH"] = settings.expand ('%(tooldir)s/bin:%(PATH)s', locals())

	## ugr: Alien is broken.
	os.environ['PERLLIB'] = settings.expand ('%(tooldir)s/lib/perl5/site_perl/5.8.6/')

	c = commands.pop (0)
	if c == 'download':
		download_sources (target_manager, commands)
	elif c == 'build':
		run_builder (settings, target_manager, commands)
	elif c == 'build-installer':
		build_installer (settings, target_manager, commands)
	elif c == 'package-installer':
		package_installers (settings)
	else:
		raise 'unknown driver command %s.' % c
		cli_parser.print_help ()
		sys.exit (2)

if __name__ == '__main__':
	main ()
