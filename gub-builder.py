#!/usr/bin/python

import optparse
import os
import re
import string
import sys
import inspect
import pickle

sys.path.insert (0, 'lib/')

from misc import *
import gup
import cross
import gub
import settings as settings_mod
import locker

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
                  choices=['lilypond_2_6', 'lilypond_2_8', 'origin', 'HEAD'])

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

    p.add_option ('--stage', action='store',
                  dest='stage', default=None,
                  help='Force rebuild of stage')

    p.add_option ('--cross-distcc-host', action='append',
                  dest='cross_distcc_hosts', default=[],
                  help='Add another cross compiling distcc host')

    p.add_option ('--native-distcc-host', action='append',
                  dest='native_distcc_hosts', default=[],
                  help='Add another native distcc host')

    p.add_option ('-V', '--verbose', action='store_true',
                  dest='verbose')

    p.add_option ('--force-package', action='store_true',
                  default=False,
                  dest='force_package',
                  help='allow packaging of tainted compiles' )

    p.add_option ('--build-source', action='store_true',
                  default=False,
                  dest='build_source',
                  help='build source packages')

    p.add_option ('--lax-checksums',
                  action='store_true',
                  default=False,
                  dest='lax_checksums',
                  help="don't rebuild packages with differing checksums")

    p.add_option ('-l', '--skip-if-locked',
                  default=False,
                  dest="skip_if_locked",
                  action="store_true",
                  help="Return successfully if another build is already running")
    p.add_option ('-j', '--jobs',
                  default="1", action='store',
                  dest='cpu_count',
                  help='set number of simultaneous jobs')

    return p

def checksums_valid (manager, specname, spec_object_dict):
    spec = spec_object_dict[specname]

    valid = True
    for package in spec.get_packages ():
        name = package.name()
        package_dict = manager.package_dict (name)

        valid = (spec.spec_checksum == package_dict['spec_checksum']
                 and spec.source_checksum () == package_dict['source_checksum'])

        hdr = package.expand ('%(split_hdr)s')
        valid = valid and os.path.exists (hdr)
        if valid:
            hdr_dict = pickle.load (open (hdr))
            hdr_sum = hdr_dict['spec_checksum']
            valid = valid and hdr_sum == spec.spec_checksum
            valid = valid and spec.source_checksum () == hdr_dict['source_checksum']

    ## let's be lenient for cross packages.
    ## spec.cross_checksum == manager.package_dict(name)['cross_checksum'])

    return valid

def run_one_builder (options, spec_obj):
    available = dict (inspect.getmembers (spec_obj, callable))
    if options.stage:
        (available[options.stage]) ()
        return

    stages = ['untar', 'patch',
              'configure', 'compile', 'install',
              'src_package', 'package', 'clean']

    if not options.build_source:
        stages.remove ('src_package')

    tainted = False
    for stage in stages:
        if (not available.has_key (stage)):
            continue

        if spec_obj.is_done (stage, stages.index (stage)):
            tainted = True
            continue

        spec_obj.os_interface.log_command (' *** Stage: %s (%s)\n'
                                           % (stage, spec_obj.name ()))

        if stage == 'package' and tainted and not options.force_package:
            msg = spec_obj.expand ('''Compile was continued from previous run.
Will not package.
Use

rm %(stamp_file)s

to force rebuild, or

--force-package

to skip this check.
''')
            spec_obj.os_interface.log_command (msg)
            raise 'abort'


        if (stage == 'clean'
            and options.keep_build):
            os.unlink (spec_obj.get_stamp_file ())
            continue

        try:
            (available[stage]) ()
        except SystemFailed:

            ## failed patch will leave system in unpredictable state.
            if stage == 'patch':
                spec_obj.system ('rm %(stamp_file)s')

            raise

        if stage != 'clean':
            spec_obj.set_done (stage, stages.index (stage))

def run_builder (options, settings, manager, names, spec_object_dict):
    PATH = os.environ['PATH']

    ## cross_prefix is also necessary for building cross packages, such as GCC
    os.environ['PATH'] = settings.expand ('%(cross_prefix)s/bin:' + PATH,
                                          locals ())

    ## UGH -> double work, see cross.change_target_packages () ?
    sdk_pkgs = [p for p in spec_object_dict.values ()
                if isinstance (p, gub.SdkBuildSpec)]
    cross_pkgs = [p for p in spec_object_dict.values ()
                  if isinstance (p, cross.CrossToolSpec)]

    extra_build_deps = [p.name () for p in sdk_pkgs + cross_pkgs]
    if not options.stage:

        reved = names[:]
        reved.reverse ()
        for spec_name in reved:
            spec = spec_object_dict[spec_name]
            checksum_ok = (options.lax_checksums
                           or checksums_valid (manager, spec_name,
                                               spec_object_dict))
            for p in spec.get_packages ():
                if (manager.is_installed (p.name ()) and
                    (not manager.is_installable (p.name ())
                     or not checksum_ok)):

                    manager.uninstall_package (p.name ())

    for spec_name in names:
        spec = spec_object_dict[spec_name]
        all_installed = True
        for p in spec.get_packages():
            all_installed = all_installed and manager.is_installed (p.name ())
        if all_installed:
            continue
        checksum_ok = (options.lax_checksums
                       or checksums_valid (manager, spec_name,
                                           spec_object_dict))

        is_installable = forall (manager.is_installable (p.name ())
                                 for p in spec.get_packages ())

        if (options.stage
            or not is_installable
            or not checksum_ok):
            settings.os_interface.log_command ('building package: %s\n'
                                               % spec_name)
            run_one_builder (options, spec)

        for p in spec.get_packages ():
            name = p.name ()
            if not manager.is_installed (name):
                manager.unregister_package_dict (p.name ())
                manager.register_package_dict (p.dict ())
                manager.install_package (p.name ())

def main ():
    cli_parser = get_cli_parser ()
    (options, files) = cli_parser.parse_args ()

    if not options.platform:
        print 'error: no platform specified'
        cli_parser.print_help ()
        sys.exit (2)

    settings = settings_mod.get_settings (options.platform)
    settings.lilypond_branch = options.lilypond_branch
    settings.build_source = options.build_source
    settings.cpu_count = options.cpu_count
    settings.set_distcc_hosts (options)
    settings.options = options ##ugh

    command = files.pop (0)

    PATH = os.environ['PATH']
    os.environ['PATH'] = settings.expand ('%(buildtools)s/bin:' + PATH)

    (package_names, spec_object_dict) = gup.get_source_packages (settings,
                                                                 files)
    if command == 'download' or command == 'build':
        def get_all_deps (name):
            package = spec_object_dict[name]
            deps = package.get_build_dependencies ()
            if not settings.is_distro:
                deps = [gup.get_base_package_name (d) for d in deps]
            return deps

        deps = gup.topologically_sorted (files, {}, get_all_deps, None)
        if options.verbose:
            print 'deps:' + `deps`

    if command == 'download':
        for i in deps:
            spec_object_dict[i].do_download ()

    elif command == 'build':
        try:
            pm = gup.get_target_manager (settings)

            ## Todo: have a readonly lock for local platform
        except locker.LockedError:
            print 'another build in progress. Skipping.'
            if options.skip_if_locked:
                sys.exit (0)
            raise

        gup.add_packages_to_manager (pm, settings, spec_object_dict)
        deps = filter (spec_object_dict.has_key, package_names)

        run_builder (options, settings, pm, deps, spec_object_dict)
    else:
        raise 'unknown gub-builder command %s.' % command
        cli_parser.print_help ()
        sys.exit (2)

if __name__ == '__main__':
    main ()
