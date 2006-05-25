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

import gup
import cross
import distcc
import framework
import gub
import installer
import settings as settings_mod
import subprocess
import pickle


def get_cli_parser ():
    p = optparse.OptionParser ()

    p.usage='''gub-builder.py [OPTION]... COMMAND [PACKAGE]...

Commands:

download          - download packages
build             - build target packages

'''
    p.description='Grand Unified Builder.  Specify --package-version to set build version'

    p.add_option ('-B', '--branch', action='store',
                  dest='lilypond_branch',
                  type='choice',
                  default='HEAD',
                  help='select lilypond branch [HEAD]',
                  choices=['lilypond_2_6', 'lilypond_2_8', 'HEAD'])
    
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
    
    p.add_option ('', '--build-source', action='store_true',
                  default=False,
                  dest='build_source',
                  help='build source packages')
    
    p.add_option ('', '--split-packages', action="store_true",
                  default=False,
                  dest='split_packages',
                  help='split Cygwin packages')
    
    p.add_option ('', '--lax-checksums',
                  action='store_true',
                  default=False,
                  dest='lax_checksums',
                  help="don't rebuild packages with differing checksums")
    
    p.add_option ('', '--skip-if-locked',
                  default=False,
                  dest="skip_if_locked",
                  action="store_true",
                  help="Return successfully if another build is already running")
    
    return p

def checksums_valid (manager, name, spec_object_dict):
    spec = spec_object_dict[name]
    package_dict =  manager.package_dict (name)
    v = (spec.spec_checksum == package_dict['spec_checksum']
         and spec.source_checksum () == package_dict['source_checksum'])

    hdr = spec.expand ('%(hdr_file)s')
    v = v and os.path.exists (hdr)
    if v:
        hdr_dict = pickle.load (open (hdr)) 
        hdr_sum = hdr_dict['spec_checksum']
        v = v and hdr_sum == spec.spec_checksum
        try:
            v = v and spec.source_checksum () == hdr_dict['source_checksum']

            ## FIXME
        except KeyError:
            pass
            
    
    ## let's be lenient for cross packages.
    ## spec.cross_checksum == manager.package_dict(name)['cross_checksum'])

    return v


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
            checksum_ok = (settings.options.lax_checksums
                   or checksums_valid (manager, p, package_object_dict))
            if (manager.is_installed (p) and
              (not manager.is_installable (p)
              or not checksum_ok)):
                manager.uninstall_package (p)

    for p in names:
        if manager.is_installed (p):
            continue
        
        checksum_ok = (settings.options.lax_checksums
                       or checksums_valid (manager, p, package_object_dict))
        if (settings.options.stage
            or not manager.is_installable (p)
            or not checksum_ok):
            settings.os_interface.log_command ('building package: %s\n'
                                               % p)
            
            package_object_dict[p].builder ()

        if (manager.is_installable (p)
            and not manager.is_installed (p)):
            spec_obj = package_object_dict[p]
            d = spec_obj.get_substitution_dict ()
            
            manager.unregister_package_dict (p)
            manager.register_package_dict (d)
            manager.install_package (p)

def main ():
    cli_parser = get_cli_parser ()
    (options, commands)  = cli_parser.parse_args ()

    if not options.platform:
        raise 'error: no platform specified'
        cli_parser.print_help ()
        sys.exit (2)

    settings = settings_mod.get_settings (options.platform)
    settings.add_options (options)
    settings.set_distcc_hosts (options)

    c = commands.pop (0)
    if not commands:
        commands = ['lilypond']


    ## crossprefix is also necessary for building cross packages,
    ## such as GCC

    PATH = os.environ['PATH']
    os.environ['PATH'] = settings.expand ('%(buildtools)s/bin:%(PATH)s',
                       locals ())

    (package_names, package_object_dict) = gup.get_packages (settings,
                                                             commands)

    if c == 'download' or c == 'build':
        def get_all_deps (name):
            package = package_object_dict[name]
            return (package.name_dependencies
                + package.name_build_dependencies)
        deps = gup.topologically_sorted (commands, {}, get_all_deps,
                         None)
        if options.verbose:
            print 'deps:' + `deps`

    if c == 'download':
        for i in deps:
            package_object_dict[i].do_download ()

    elif c == 'build':
        try:
            pm = gup.get_target_manager (settings)
        except gup.LockError:
            print 'another build in progress. Skipping.'
            if options.skip_if_locked:
                sys.exit (0)
            raise 
            

        # FIXME: what happens here, {cross, cross_module}.packages
        # are already added?
        gup.add_packages_to_manager (pm, settings, package_object_dict)
        deps = filter (package_object_dict.has_key, package_names)
        deps = filter (pm.is_registered, deps)

        run_builder (settings, pm, deps, package_object_dict)
    else:
        raise 'unknown gub-builder command %s.' % c
        cli_parser.print_help ()
        sys.exit (2)

if __name__ == '__main__':
    main ()
