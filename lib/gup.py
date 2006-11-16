import gdbm as dbmodule
#import dbhash as dbmodule

import pickle
import os
import re
import string
import fcntl
import sys
import glob

#
import cross
import targetpackage
from misc import *  # URG, fixme
import locker
import cygwin
import debian
import gub ## ugh

class GupException (Exception):
    pass

class FileManager:

    """FileManager handles a tree, and keeps track of files,
    associating files with a package name"""

    def __init__ (self, root, os_interface, dbdir=None, clean=False):
        self.root = os.path.normpath (root)
        if dbdir:
            self.config = dbdir
        else:
            self.config = self.root + '/etc/gup'

        self.config = os.path.normpath (self.config)
        self.os_interface = os_interface
        self.verbose = True
        self.is_distro = False

        ## lock must be outside of root, otherwise we can't rm -rf root
        self.lock = locker.Locker (self.root + '.lock')
        if clean:
            os_interface.system ('rm -fr %s' % self.config)
            os_interface.system ('rm -fr %s' % self.root)
            
        self.make_dirs ()
        self._file_package_db = dbmodule.open (self.config
                           + '/files.db', 'c')
        self._package_file_db = dbmodule.open (self.config
                           + '/packages.db', 'c')

    def __repr__ (self):
        name = self.__class__.__name__
        root = self.root
        distro =  self.is_distro
        return '%(name)s: %(root)s, distro: %(distro)d'  % locals()

    def make_dirs (self):
        if not os.path.isdir (self.config):
            self.os_interface.system ('mkdir -p %s' % self.config)
        if not os.path.isdir (self.root):
            self.os_interface.system ('mkdir -p %s' % self.root)
        
    def tarball_files (self, ball):
        flag = tar_compression_flag (ball)
        str = self.os_interface.read_pipe ('tar -t%(flag)sf "%(ball)s"'
                                           % locals ())
        lst = str.split ('\n')
        return lst

    def installed_files (self, package):
        return self._package_file_db[package].split ('\n')

    def is_installed (self, name):
        return self._package_file_db.has_key (name)

    def install_tarball (self, ball, name):
        self.os_interface.log_command ('installing package %(name)s from %(ball)s\n'
                                       % locals ())

        flag = tar_compression_flag (ball)
        root = self.root
        lst = self.tarball_files (ball)

        conflicts = False
        for f in lst:
            if (self._file_package_db.has_key (f)
                and not os.path.isdir (self.root + '/' +  f)):
                print 'already have file %s: %s' % (f, self._file_package_db[f])
                conflicts = True

        if conflicts and not self.is_distro:
            raise Exception ('abort')

        self.os_interface.system ('tar -C %(root)s -x%(flag)sf %(ball)s'
                                  % locals ())

        self._package_file_db[name] = '\n'.join (lst)
        for f in lst:
            # ignore directories.
            if not f.endswith ('/'):
                self._file_package_db[f] = name
            if f.endswith ('.la'):
                self.libtool_la_fixup (root, f)

    def libtool_la_fixup (self, root, file):
        # avoid using libs from build platform, by adding
        # %(system_root)s
        if file.startswith ('./'):
            file = file[2:]
        dir = os.path.dirname (file)
        self.os_interface.file_sub ([('^libdir=.*',
                                      """libdir='%(root)s/%(dir)s'""" % locals ()
                                      ),],
                                    '%(root)s/%(file)s' % locals ())

    def uninstall_package (self, name):
        self.os_interface.log_command ('uninstalling package: %s\n' % name)

        lst = self.installed_files (name)

        dirs = []
        files = []
        for i in lst:
            f = os.path.join (self.root, i)
            if os.path.islink (f):
                files.append (f)
            elif (not os.path.exists (f)
               and not self.is_distro):
                print 'FileManager: uninstall: %s' % name
                print 'FileManager: no such file: %s' % f
            elif os.path.isdir (f):
                dirs.append (f)
            else:
                files.append (f)

        for f in files:
            os.unlink (f)

        for d in reversed (dirs):
            try:
                os.rmdir (d)
            except OSError:
                print 'warning: %s not empty' % d

        for f in lst:

            ## fixme (?)  -- when is f == ''
            if not f or f.endswith ('/'):
                continue

            try:
                del self._file_package_db[f]
            except:
                print 'db delete failing for ', f
        del self._package_file_db[name]

    def installed_packages (self):
        names = self._package_file_db.keys ()
        return names

class PackageDictManager:
    """

    A dict of PackageName ->  (Key->Value dict)

    which can be read off the disk.
    """
    def __init__ (self, os_interface):
        self._packages = {}

        ## ugh mi 
        self.verbose = False
        
        ## ugh: mi overwrite.
        self.os_interface = os_interface
    def register_package_dict (self, d):
        nm = d['name']
        if d.has_key ('split_name'):
            nm = d['split_name']
        if (self._packages.has_key (nm)):
            if self._packages[nm]['spec_checksum'] != d['spec_checksum']:
                self.os_interface.log_command ('******** checksum of %s changed!\n\n' % nm)

            ## UGH ; need to look at installed hdr.
            if self._packages[nm]['cross_checksum'] != d['cross_checksum']:
                self.os_interface.log_command ('******** checksum of cross changed for %s\n' % nm)
            return

        self._packages[nm] = d
   
        
    def register_package_header (self, package_hdr, branch):
        if self.verbose:
            self.os_interface.log_command ('reading package header: %s\n'
                                           % `package_hdr`)

        str = open (package_hdr).read ()

        d = pickle.loads (str)

        ### FIXME - lilypond hardcoded.
        if (d['basename'] == 'lilypond'
            and branch != d['vc_branch']):
            suffix = d['vc_branch']
            print 'ignoring header: ' + package_hdr
            print 'branch: %(branch)s, suffix: %(suffix)s' % locals ()
            return

        name = d['split_name']
        if 0:
          ## FIXME ?
          if self._package_dict_db.has_key (name):
              if str != self._package_dict_db[name]:
                  self.os_interface.log_command ("package header changed for %s\n" % name)

              return

        self.register_package_dict (d)

    def unregister_package_dict (self, name):
        del self._packages[name]

    def is_registered (self, package):
        return self._packages.has_key (package)

    def package_dict (self, package_name):
        return self._packages[package_name]

    def get_all_packages (self):
        return self._packages.values ()

    def is_installable (self, name):
        d = self._packages[name]
        ball = '%(split_ball)s' % d
        hdr = '%(split_hdr)s' % d
        return os.path.exists (ball) and os.path.exists (hdr)

    def read_package_headers (self, s, branch):
        if os.path.isdir (s) and not s.endswith ('/'):
            s += '/'
            
        for f in glob.glob ('%(s)s*hdr' % locals ()):
            self.register_package_header (f, branch)


## FIXME: MI
class PackageManager (FileManager, PackageDictManager):


    """PackageManager is a FileManager, which also associates a
    key/value dict with each package.

    Such dicts come either from either 

    1. A build spec (ie. a python object)

    2. A pickled dict on disk, a package header

    3. 
    """

    
    def __init__ (self, root, os_interface, **kwargs):
        FileManager.__init__ (self, root, os_interface, **kwargs)
        PackageDictManager.__init__ (self, os_interface)
        
        self._package_dict_db = dbmodule.open (self.config
                           + '/dicts.db', 'c')
        for k in self._package_dict_db.keys ():
            v = self._package_dict_db[k]
            self.register_package_dict (pickle.loads (v))

    def installed_package_dicts (self):
        names = self._package_file_db.keys ()
        return [self._packages[p] for p in names]

    def install_package (self, name):
        if self.is_installed (name):
            return
        self.os_interface.log_command ('installing package: %s\n'
                                       % name)
        if self._package_file_db.has_key (name):
            print 'already have package ', name
            raise Exception ('abort')
        d = self._packages[name]
        ball = '%(split_ball)s' % d
        self.install_tarball (ball, name)
        self._package_dict_db[name] = pickle.dumps (d)

    def uninstall_package (self, name):
        FileManager.uninstall_package (self, name)
        del self._package_dict_db[name]

    
def is_string (x):
    return type (x) == type ('')

class DependencyManager (PackageManager):

    """Manage packages that have dependencies and
    build_dependencies in their package dicts"""

    def __init__ (self, root, os_interface, **kwargs):
        PackageManager.__init__ (self, root, os_interface, **kwargs)
        self.include_build_deps = True

    def dependencies (self, name):
        assert is_string (name)
        try:
            return self.dict_dependencies (self._packages[name])
        except KeyError:
            print 'unknown package', name
            return []

    def dict_dependencies (self, dict):
        deps = dict['dependencies_string'].split (';')
        if self.include_build_deps:
            deps += dict['build_dependencies_string'].split (';')

        deps = [d for d in deps if d]
        return deps

################
# UGh moveme

def topologically_sorted_one (todo, done, dependency_getter,
                              recurse_stop_predicate=None):
    sorted = []
    if done.has_key (todo):
        return sorted

    done[todo] = 1

    deps = dependency_getter (todo)
    for d in deps:
        if recurse_stop_predicate and recurse_stop_predicate (d):
            continue

        assert type (d) == type (todo)

        sorted += topologically_sorted_one (d, done, dependency_getter,
                                            recurse_stop_predicate=recurse_stop_predicate)

    sorted.append (todo)
    return sorted

def topologically_sorted (todo, done, dependency_getter,
             recurse_stop_predicate=None):
    s = []
    for t in todo:
        s += topologically_sorted_one (t, done, dependency_getter,
                                       recurse_stop_predicate)

    return s


    

################################################################
# UGH
# this is too hairy. --hwn

def gub_to_distro_deps (deps, gub_to_distro_dict):
    distro = []
    for i in deps:
        if i in gub_to_distro_dict.keys ():
            distro += gub_to_distro_dict[i]
        else:
            distro += [i]
    return distro

def get_base_package_name (name):
    name = re.sub ('-devel$', '', name)

    # breaks mingw dep resolution, mingw-runtime
    ##name = re.sub ('-runtime$', '', name)
    name = re.sub ('-doc$', '', name)
    return name

def get_source_packages (settings, todo):
    """TODO is a list of (source) buildspecs.

Generate a list of BuildSpec needed to build TODO, in
topological order
    
"""

    ## don't modify
    todo = todo[:]

    
    cross_packages = cross.get_cross_packages (settings)
    spec_dict = dict ((p.name (), p) for p in cross_packages)
    todo += spec_dict.keys ()

    def name_to_dependencies_via_gub (name):
        name = get_base_package_name (name)
        if spec_dict.has_key (name):
            spec = spec_dict[name]
        else:
            spec = targetpackage.load_target_package (settings, name)
            spec_dict[name] = spec

        return map (get_base_package_name, spec.get_build_dependencies ())

    def name_to_dependencies_via_distro (distro_packages, name):
        if spec_dict.has_key (name):
            spec = spec_dict[name]
        else:
            if name in todo or name not in distro_packages.keys ():
                spec = targetpackage.load_target_package (settings, name)
            else:
                spec = distro_packages[name]
            spec_dict[name] = spec
        return spec.get_build_dependencies ()

    def name_to_dependencies_via_cygwin (name):
        return name_to_dependencies_via_distro (cygwin.get_packages (), name)

    def name_to_dependencies_via_debian (name):
        return name_to_dependencies_via_distro (debian.get_packages (), name)

    name_to_deps = name_to_dependencies_via_gub
    if settings.platform == 'cygwin':
        cygwin.init_dependency_resolver (settings)
        name_to_deps = name_to_dependencies_via_cygwin
    elif settings.platform in ('arm', 'debian', 'mipsel'):
        debian.init_dependency_resolver (settings)
        name_to_deps = name_to_dependencies_via_debian

    spec_names = topologically_sorted (todo, {}, name_to_deps)
    spec_dict = dict ((n, spec_dict[n]) for n in spec_names)
    cross.set_cross_dependencies (spec_dict)

    if settings.is_distro:
        def obj_to_dependency_objects (obj):
            return [spec_dict[n] for n in obj.get_build_dependencies ()]
    else:
        def obj_to_dependency_objects (obj):
            return [spec_dict[get_base_package_name (n)]
                    for n in obj.get_build_dependencies ()]

    spec_objs = topologically_sorted (spec_dict.values (), {},
                                      obj_to_dependency_objects)

    sorted_names = [o.name () for o in spec_objs]
    return (sorted_names, spec_dict)

def get_target_manager (settings):
    target_manager = DependencyManager (settings.system_root,
                      settings.os_interface)
    return target_manager

def add_packages_to_manager (target_manager, settings, package_object_dict):
    
    ## Ugh, this sucks: we now have to have all packages
    ## registered at the same time.
    
    for spec in package_object_dict.values ():
        for package in spec.get_packages ():
            target_manager.register_package_dict (package.dict ())

    return target_manager
