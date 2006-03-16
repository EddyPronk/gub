#!/usr/bin/python

import __main__
import optparse
import os
import re
import string
import sys
import inspect
import types

sys.path.insert (0, 'lib/')

import gup2
import cross
import distcc
import framework
import gub
import installer
import settings as settings_mod
import subprocess

def get_settings (platform):
	settings = settings_mod.Settings (platform)
	
	if platform not in settings_mod.platforms.keys ():
		raise 'unknown platform', platform
		
	if platform == 'darwin-ppc':
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

	def hosts (xs):
		return reduce (lambda x,y: x+y,
			       [ h.split (',') for h in xs], [])
	settings.cross_distcc_hosts = ' '.join (distcc.live_hosts (hosts (options.cross_distcc_hosts)))
	settings.native_distcc_hosts = ' '.join (distcc.live_hosts (hosts (options.native_distcc_hosts), port=3632))
	
def get_cli_parser ():
	p = optparse.OptionParser ()

	p.usage="""driver.py [OPTION]... COMMAND [PACKAGE]...

Commands:

download          - download packages
build             - build target packages
build-installer   - build installer root
strip-installer   - strip installer root
package-installer - build installer binary

"""
	p.description='Grand Unified Builder.  Specify --package-version to set build version'

	p.add_option ('-B', '--branch', action='store',
		      dest='lilypond_branch',
		      type='choice',
		      default='HEAD',
		      help='select lilypond branch [HEAD]',
		      choices=['lilypond_2_6', 'HEAD'])
	p.add_option ('', '--installer-version', action='store',
		      default='0.0.0',
		      dest='installer_version')
	p.add_option ('', '--installer-build', action='store',
		      default='0',
		      dest='installer_build')
	p.add_option ('-k', '--keep', action='store_true',
		      dest='keep_build',
		      default=None,
		      help='leave build and src dir for inspection')
	p.add_option ('-p', '--target-platform', action='store',
		      dest='platform',
		      type='choice',
		      default=None,
		      help='select target platform',
		      choices=settings_mod.platforms.keys ())
	p.add_option ('-s', '--setting', action='append',
		      dest='settings',
		      type='string',
		      default=[],
		      help='add a variable')
	p.add_option ('', '--stage', action='store',
		      dest='stage', default=None,
		      help='Force rebuild of stage')
	
	p.add_option ('', '--cross-distcc-host', action='append',
		      dest='cross_distcc_hosts', default=[],
		      help='Add another cross compiling distcc host')

	p.add_option ('', '--native-distcc-host', action='append',
		      dest='native_distcc_hosts', default=[],
		      help='Add another native distcc host')
	
	p.add_option ('-V', '--verbose', action='store_true',
		      dest='verbose')
	p.add_option ('', '--force-package', action='store_true',
		      default=False,
		      dest='force_package',
		      help='allow packaging of tainted compiles' )
	return p

def build_installer (settings, args):
	settings.os_interface.system (settings.expand ('rm -rf %(installer_root)s'))
	settings.os_interface.system (settings.expand ('rm -rf %(installer_db)s'))
	
	install_manager = gup2.Dependency_manager (settings.installer_root,
						   settings.os_interface,
						   dbdir=settings.installer_db)
	install_manager.include_build_deps = False
	install_manager.read_package_headers (settings.gub_uploads)
	install_manager.read_package_headers (settings.gub_cross_uploads)

	def get_dep (x):
		return install_manager.dependencies (x)
	
	package_names = gup2.topologically_sorted (args, {},
						   get_dep,
						   None)

	def is_sdk (x):
		try:
			return install_manager.package_dict (p)['is_sdk_package'] == 'true'
		except KeyError:
			# ugh.
			return (x in ['darwin-sdk', 'w32api', 'freebsd-runtime',
				      'mingw-runtime', 'libc6', 'libc6-dev', 'linux-kernel-headers',
				      ])
		
	package_names = [p for p in package_names
			 if not is_sdk (p)]

	for a in package_names:
		install_manager.install_package (a)

def strip_installer (settings, installers):
	for p in installers:
		settings.os_interface.log_command (' ** Stage: %s (%s)\n'
						   % ('strip', p.name ()))
		p.strip ()

def package_installer (settings, installers):
	for p in installers:
		settings.os_interface.log_command (' *** Stage: %s (%s)\n'
						   % ('create', p.name ()))
		p.create ()
		
def installer_command (c, settings, args):
	if c == 'build-installer':
		build_installer (settings, args)
		return
	
	installers = installer.get_installers (settings, args)
	if c == 'strip-installer':
		strip_installer (settings, installers)
	elif c == 'package-installer':
		package_installer (settings, installers)
	else:
		raise 'unknown installer command', c
	
def run_builder (settings, manager, names, package_object_dict):
	PATH = os.environ['PATH']

	## crossprefix is also necessary for building cross packages, such as GCC
	os.environ['PATH'] = settings.expand ('%(crossprefix)s/bin:%(PATH)s',
					      locals ())


	## UGH -> double work, see cross.change_target_packages () ?
	sdk_pkgs = [p for p in package_object_dict.values ()
		    if isinstance (p, gub.Sdk_package)]
	cross_pkgs = [p for p in package_object_dict.values ()
		      if isinstance (p, cross.Cross_package)]

	extra_build_deps = [p.name () for p in sdk_pkgs + cross_pkgs]
	framework.package_fixups (settings, package_object_dict.values (),
				  extra_build_deps)

	if not settings.options.stage:
		reved = names[:]
		reved.reverse ()
		for p in reved:
			if (manager.is_installed (p) and
			    not manager.is_installable (p)):
				manager.uninstall_package (p)

	for p in names:
		if manager.is_installed (p):
			continue
		
		if not manager.is_installable (p):
			settings.os_interface.log_command ('building package: %s\n'
							   % p)
			
			package_object_dict[p].builder ()
			
		if (manager.is_installable (p)
		    and not manager.is_installed (p)):
			manager.install_package (p)

def main ():
	cli_parser = get_cli_parser ()
	(options, commands)  = cli_parser.parse_args ()

	if not options.platform:
		raise 'error: no platform specified'
		cli_parser.print_help ()
		sys.exit (2)

	settings = get_settings (options.platform)
	add_options (settings, options)

	c = commands.pop (0)
	if not commands:
		commands = ['lilypond']


	## crossprefix is also necessary for building cross packages,
	## such as GCC

	PATH = os.environ['PATH']
	os.environ['PATH'] = settings.expand ('%(buildtools)s/bin:%(PATH)s',
					      locals ())

	if c in ('clean-installer', 'build-installer', 'strip-installer', 'package-installer'):
		installer_command (c, settings, commands)
		return

	(package_names, package_object_dict) = gup2.get_packages (settings,
								  commands)
	if c == 'download' or c == 'build':
		def get_all_deps (name):
			package = package_object_dict[name]
			return (package.name_dependencies
				+ package.name_build_dependencies)
		deps = gup2.topologically_sorted (commands, {}, get_all_deps,
						  None)
		if options.verbose:
			print 'deps:' + `deps`

	if c == 'download':
		for i in deps:
			package_object_dict[i].do_download ()

	elif c == 'build':
		pm = gup2.get_target_manager (settings)
		# FIXME: what happens here, {cross, cross_module}.packages
		# are already added?
		gup2.add_packages_to_manager (pm, settings, package_object_dict)
		deps = filter (package_object_dict.has_key, package_names)
		deps = filter (pm.is_registered, deps)

		run_builder (settings, pm, deps, package_object_dict)
	else:
		raise 'unknown driver command %s.' % c
		cli_parser.print_help ()
		sys.exit (2)

if __name__ == '__main__':
	main ()
