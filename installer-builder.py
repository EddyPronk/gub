#!/usr/bin/python

import optparse
import os
import sys
import pickle

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

    p.add_option ('-B', '--branch', 
                  dest='branches',
                  default=[],
                  action='append',
                  help='set branch for package')

    p.add_option ('-l', '--skip-if-locked',
                  default=False,
                  dest="skip_if_locked",
                  action="store_true",
                  help="Return successfully if another build is already running")

    p.add_option ('--version-db', action='store',
                  default='uploads/lilypond.versions',
                  dest='version_db')

    p.add_option ("--no-strip", action="store_false",
                  default=True,
                  dest="do_strip",
                  help="don't perform strip stage")
                  
    p.add_option ("--setting", '-s',
                  action="append",
                  default=[],
                  dest="settings",
                  help="extra overrides for settings")

                  
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

def check_installer (installer, options, args):
    settings = installer.settings
    install_manager = gup.PackageDictManager (settings.os_interface)
    install_manager.read_package_headers (settings.gub_uploads,
                                          settings.branch_dict)

    ## can't interrogate installer yet, because version is not known yet.
    file = installer.installer_checksum_file
    if not os.path.exists (file):
        return False
    
    checksum = pickle.loads (open (file).read ())
    ok = True
    for (p, source_hash, spec_hash) in checksum:
        dict = install_manager.package_dict (p)
        ok = (ok
              and source_hash == dict['source_checksum']
              and spec_hash == dict['spec_checksum'])

    return ok
         
def build_installer (installer, args, options):
    settings = installer.settings
    
    install_manager = gup.DependencyManager (installer.installer_root,
                                             settings.os_interface,
                                             dbdir=installer.installer_db,
                                             clean=True)
    
    install_manager.include_build_deps = False
    install_manager.read_package_headers (settings.gub_uploads,
                                          settings.branch_dict)

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

    settings.installer_version = version
    settings.installer_build = buildnumber


    checksum_list = []
    for p in install_manager.installed_packages():
        dict = install_manager.package_dict (p)
        checksum_list.append ((p, 
                               dict['source_checksum'],
                               dict['spec_checksum']))
    
    installer.checksum = pickle.dumps (checksum_list)

def strip_installer (obj):
    obj.log_command (' ** Stage: %s (%s)\n'
                     % ('strip', obj.name))
    obj.strip ()

def package_installer (installer):
    
    installer.create ()
        
def run_installer_commands (commands, settings, args, options):
    
    installer_obj = installer.get_installer (settings, args)
    installer_obj.name = args[0]

    ## UGH -  we don't have the package dicts yet.
    installer_obj.pretty_name = {
        'lilypond': 'LilyPond',
        'git': 'Git',
        }[args[0]]
    installer_obj.package_branch = settings.branch_dict[args[0]]
    installer_obj.installer_root = settings.targetdir + '/installer-%s-%s' % (args[0],
                                                                              installer_obj.package_branch)
    installer_obj.installer_checksum_file = installer_obj.installer_root + '.checksum'
    installer_obj.installer_db = installer_obj.installer_root + '-dbdir'
    
    if check_installer (installer_obj, options, args):
        print 'installer is up to date'
        return 

    for c in commands:
        print (' *** Stage: %s (%s)\n'
               % (c, installer_obj.name))
    
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

    settings.set_branches (options.branches)
    for s in options.settings:
        (k, v) = tuple (s.split ('='))
        if settings.__dict__.has_key (k):
            print "warning overwriting %s = %s with %s" % (k, settings.__dict__[k], v)
            
        settings.__dict__[k] = v
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



