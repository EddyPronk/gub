#!/usr/bin/python

import optparse
import os
import sys
import md5

sys.path.insert (0, 'lib/')

import gup
import cross
import installer
import settings as settings_mod
import locker
import misc
import versiondb

def parse_command_line ():
    p = optparse.OptionParser ()

    p.usage='''installer-builder.py [OPTION]... COMMAND [PACKAGE]

Commands:

build     - build installer root
strip     - strip installer root
package   - package installer binary
build-all - build, strip, package

'''
    p.description='Grand Unified Builder - collect in platform dependent package format'

    p.add_option ('-B', '--branch', action='store',
                  dest='lilypond_branch',
                  default='origin',
                  help='select lilypond branch [origin]')
    
    p.add_option ('-l', '--skip-if-locked',
                  default=False,
                  dest="skip_if_locked",
                  action="store_true",
                  help="Return successfully if another build is already running")

    p.add_option ('--version-db', action='store',
                  default='uploads/versions.db',
                  dest='version_db')

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

    
    return (options, args)


def build_installer (installer, args, options):
    settings = installer.settings
    
    install_manager = gup.DependencyManager (installer.installer_root,
                                             settings.os_interface,
                                             dbdir=installer.installer_db,
                                             clean=True)
    
    install_manager.include_build_deps = False
    install_manager.read_package_headers (settings.gub_uploads,
                                          settings.lilypond_branch)

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


    version = install_manager.package_dict (args[0])['version']
    version_tup = tuple (map (int, version.split ('.')))

    db = versiondb.VersionDataBase (options.version_db)
    buildnumber = '%d' % db.get_next_build_number (version_tup)

    ## ugh: naming consistency.
    installer.lilypond_version = version
    installer.lilypond_build = buildnumber
    settings.installer_version = version
    settings.installer_build = buildnumber


    cs = md5.new()
    for dict in sorted (install_manager.installed_package_dicts ()):
        cs.update (dict['source_checksum'])
        cs.update (dict['spec_checksum'])
    
    installer.checksum = cs.hexdigest ()

def strip_installer (obj):
    obj.log_command (' ** Stage: %s (%s)\n'
                     % ('strip', obj.name ()))
    obj.strip ()

def package_installer (installer):
    
    installer.create ()
        
def run_installer_commands (commands, settings, args, options):
    installer_obj = installer.get_installer (settings, args)
    for c in commands:
        print (' *** Stage: %s (%s)\n'
               % (c, installer_obj.name ()))
    
        if c == ('build'):
            build_installer (installer_obj, args, options)
        elif c == ('strip'):
            strip_installer (installer_obj)
        elif c == ('package'):
            package_installer (installer_obj)
        else:
            raise  Exception ('unknown installer command', c)


def main ():
    (options, commands)  = parse_command_line ()

    settings = settings_mod.get_settings (options.platform)
    settings.lilypond_branch = options.lilypond_branch
                  
    c = commands.pop (0)

    cs = [c]
    if c == 'build-all':
        cs = ['build', 'strip', 'package']

        if not  options.do_strip:
            cs.remove ('strip')
        
    try:
        run_installer_commands (cs, settings, commands, options)
    except locker.LockedError:
        if options.skip_if_locked:
            print 'skipping build; install_root is locked'
            sys.exit (0)
        raise

if __name__ == '__main__':
    main ()



