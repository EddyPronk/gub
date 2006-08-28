#!/usr/bin/python

import optparse
import os
import sys

sys.path.insert (0, 'lib/')

import gup
import cross
import installer
import settings as settings_mod
import locker
import misc

def parse_command_line ():
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

    p.add_option ('-v', '--version-file', action='store',
                  default='',
                  dest='version_file')
    
    p.add_option ('-b', '--buildnumber-file', action='store',
                  default='',
                  dest='build_file')

    p.add_option ("--no-strip", action="store_false",
                  default=True,
                  dest="do_strip",
                  help="don't perform strip stage")
                  
    p.add_option ('-p', '--target-platform', action='store',
                  dest='platform',
                  type='choice',
                  default=None,
                  help='select target platform',
                  choices=settings_mod.platforms.keys ())

    (options, args) = p.parse_args ()

    if not options.platform:
        raise Exception ('error: no platform specified')
        cli_parser.print_help ()
        sys.exit (2)

    
    options.installer_version = '0.0.0'
    options.installer_build = '0'

    if options.build_file:
        options.installer_build = misc.grok_sh_variables (options.build_file)['INSTALLER_BUILD']
    
    if options.version_file:
        d = misc.grok_sh_variables (options.version_file)
        options.installer_version = ('%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d)

    print "Using version number", options.installer_version, options.installer_build

    return (options, args)


def build_installer (installer, args):
    settings = installer.settings
    
    install_manager = gup.DependencyManager (installer.expand ('%(installer_root)s'),
                                             settings.os_interface,
                                             dbdir=installer.expand ('%(installer_db)s'),
                                             clean=True)
    
    install_manager.include_build_deps = False
    install_manager.read_package_headers (installer.expand ('%(gub_uploads)s'), settings.lilypond_branch)

    def get_dep (x):
        return install_manager.dependencies (x)
    
    package_names = gup.topologically_sorted (args, {},
                                              get_dep,
                                              None)

    # WTF is gcc-runtime?  Add to package dependencies, if necessary
    if not settings.is_distro:
        package_names += ["gcc-runtime"]

    for a in package_names:
        install_manager.install_package (a)

    installer.use_install_root_manager (install_manager)
    

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
    (options, commands)  = parse_command_line()

    settings = settings_mod.get_settings (options.platform)
    settings.installer_version = options.installer_version
    settings.installer_build = options.installer_build
    settings.lilypond_branch = options.lilypond_branch
                  
    c = commands.pop (0)

    ## cross_prefix is also necessary for building cross packages,
    ## such as GCC

    PATH = os.environ['PATH']
    os.environ['PATH'] = settings.expand ('%(buildtools)s/bin:' + PATH)

    cs = [c]
    if c == 'build-all':
        cs = ['build', 'strip', 'package']

        if not  options.do_strip:
            cs.remove ('strip')
        
    try:
        run_installer_commands (cs, settings, commands)
    except locker.LockedError:
        if options.skip_if_locked:
            print 'skipping build; install_root is locked'
            sys.exit (0)
        raise

if __name__ == '__main__':
    main ()
