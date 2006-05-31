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
    
    p.add_option ('-l', '--skip-if-locked',
                  default=False,
                  dest="skip_if_locked",
                  action="store_true",
                  help="Return successfully if another build is already running")

    p.add_option ('-v', '--installer-version', action='store',
                  default='0.0.0',
                  dest='installer_version')
    
    p.add_option ('-b', '--installer-build', action='store',
                  default='0',
                  dest='installer_build')

    p.add_option ('-p', '--target-platform', action='store',
                  dest='platform',
                  type='choice',
                  default=None,
                  help='select target platform',
                  choices=settings_mod.platforms.keys ())
    return p


def build_installer (installer, args):
    settings = installer.settings
    
    installer.system ('rm -rf %(installer_root)s')
    installer.system ('rm -rf %(installer_db)s')
    
    install_manager = gup.DependencyManager (installer.expand ('%(installer_root)s'),
                                             settings.os_interface,
                                             dbdir=installer.expand ('%(installer_db)s'))
    
    install_manager.include_build_deps = False
    install_manager.read_package_headers (installer.expand ('%(gub_uploads)s'), settings.lilypond_branch)
    
    ## fixme
    #    install_manager.read_package_headers (self.expand ('%(gub_uploads)s'),  settings.lilypond_branch)

    def get_dep (x):
        return install_manager.dependencies (x)
    
    package_names = gup.topologically_sorted (args, {},
                                              get_dep,
                                              None)

    ## fixme: should split GCC in gcc and gcc-runtime.
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


def strip_installer (obj):
    obj.log_command (' ** Stage: %s (%s)\n'
                           % ('strip', obj.name ()))
    obj.strip ()

def package_installer (installer):
    installer.create ()
        
def run_installer_commands (commands, settings, args):
    installer_obj = installer.get_installer (settings, args)
    for c in commands:
        installer_obj.log_command (' *** Stage: %s (%s)\n'
                                   % (c, installer_obj.name ()))
    
        if c == ('build'):
            build_installer (installer_obj, args)
        elif c == ('strip'):
            strip_installer (installer_obj)
        elif c == ('package'):
            package_installer (installer_obj)
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
    settings.installer_version = options.installer_version
    settings.installer_build = options.installer_build
    settings.lilypond_branch = options.lilypond_branch
                  
    c = commands.pop (0)

    ## crossprefix is also necessary for building cross packages,
    ## such as GCC

    PATH = os.environ['PATH']
    os.environ['PATH'] = settings.expand ('%(buildtools)s/bin:' + PATH)

    cs = [c]
    if c == 'build-all':
        cs = ['build', 'strip', 'package']
    try:
        run_installer_commands (cs, settings, commands)
    except gup.LockError:
        if options.skip_if_locked:
            print 'skipping build; install_root is locked'
            sys.exit (0)
        raise

if __name__ == '__main__':
    main ()
