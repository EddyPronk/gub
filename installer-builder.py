#!/usr/bin/python

import optparse
import os
import sys

sys.path.insert (0, 'lib/')

import gup
import cross
import installer
import settings as settings_mod


def get_cli_parser ():
    p = optparse.OptionParser ()

    p.usage='''gub-builder.py [OPTION]... COMMAND [PACKAGE]...

Commands:

build   - build installer root
strip   - strip installer root
package - build installer binary

'''
    p.description='Grand Unified Builder - collect in platform dependent package format'

    p.add_option ('-B', '--branch', action='store',
                  dest='lilypond_branch',
                  type='choice',
                  default='HEAD',
                  help='select lilypond branch [HEAD]',
                  choices=['lilypond_2_6', 'lilypond_2_8', 'HEAD'])
    
    p.add_option ('', '--installer-version', action='store',
                  default='0.0.0',
                  dest='installer_version')
    
    p.add_option ('', '--installer-build', action='store',
                  default='0',
                  dest='installer_build')

    p.add_option ('-p', '--target-platform', action='store',
                  dest='platform',
                  type='choice',
                  default=None,
                  help='select target platform',
                  choices=settings_mod.platforms.keys ())
    return p


def build_installer (settings, args):
    settings.os_interface.system (settings.expand ('rm -rf %(installer_root)s'))
    settings.os_interface.system (settings.expand ('rm -rf %(installer_db)s'))
    
    install_manager = gup.DependencyManager (settings.installer_root,
                                             settings.os_interface,
                                             dbdir=settings.installer_db)
    install_manager.include_build_deps = False
    install_manager.read_package_headers (settings.gub_uploads, settings.lilypond_branch)
    install_manager.read_package_headers (settings.gub_cross_uploads, settings.lilypond_branch)

    def get_dep (x):
        return install_manager.dependencies (x)
    
    package_names = gup.topologically_sorted (args, {},
                                              get_dep,
                                              None)

    package_names += [p.name() for p in cross.get_cross_packages (settings)]
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
    if c == 'build':
        build_installer (settings, args)
        return
    
    installers = installer.get_installers (settings, args)
    if c == 'strip':
        strip_installer (settings, installers)
    elif c == 'package':
        package_installer (settings, installers)
    else:
        raise  Exception ('unknown installer command', c)


def main ():
    cli_parser = get_cli_parser ()
    (options, commands)  = cli_parser.parse_args ()

    if not options.platform:
        raise Exception ('error: no platform specified')
        cli_parser.print_help ()
        sys.exit (2)

    settings = settings_mod.get_settings (options.platform)
    settings.add_options (options)

    c = commands.pop (0)

    ## crossprefix is also necessary for building cross packages,
    ## such as GCC

    PATH = os.environ['PATH']
    os.environ['PATH'] = settings.expand ('%(buildtools)s/bin:' + PATH)

    print c
    if c in ('clean', 'build', 'strip', 'package'):
        installer_command (c, settings, commands)
        return

if __name__ == '__main__':
    main ()
