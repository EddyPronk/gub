# tools python has no gdbm, breaks simple home python/lilypond build
# but dbhash seems to break in odd ways:
#  File "bsddb/dbutils.py", line 62, in DeadlockWrap
#  DBPageNotFoundError: (-30987, 'DB_PAGE_NOTFOUND: Requested page not found')

import gdbm as dbmodule
#import dbhash as dbmodule

import fcntl
import glob
import os
import pickle
import re
import string
import sys

#
from gub import build
from gub import cross
from gub import dependency
from gub import locker
from gub import logging
from gub import loggedos
from gub import misc
import gub.settings
from gub import target

class GupException (Exception):
    pass

class FileManager:

    """FileManager handles a tree, and keeps track of files,
    associating files with a package name"""

    def __init__ (self, root, dbdir=None, clean=False):
        self.root = os.path.normpath (root)
        if dbdir:
            self.config = dbdir
        else:
            self.config = self.root + '/etc/gup'

        self.config = os.path.normpath (self.config)
        self.verbose = True
        self.is_distro = False

        ## lock must be outside of root, otherwise we can't rm -rf root
        self.lock_file = self.root + '.lock'
        if self.root == os.environ['HOME']:
            self.lock_file = self.root + '/.gub.lock'
        self.lock = locker.Locker (self.lock_file)
        if clean:
            loggedos.system (logging.default_logger,
                             'rm -fr %s' % self.config)
            
        self.make_dirs ()
        files_db = self.config + '/files.db'
        packages_db = self.config + '/packages.db'
        self._file_package_db = dbmodule.open (files_db, 'c')
        self._package_file_db = dbmodule.open (packages_db, 'c')
        #except DBInvalidArgError:
        # import gdmb
        # file_db = gdbm.open (file_db, 'c')
        # packages_db = gdbm.open (packages_db, 'c')
            
    def __repr__ (self):
        name = self.__class__.__name__
        root = self.root
        distro =  self.is_distro
        return '%(name)s: %(root)s, distro: %(distro)d'  % locals ()

    def make_dirs (self):
        if not os.path.isdir (self.config):
            loggedos.system (logging.default_logger,
                             'mkdir -p %s' % self.config)
        if not os.path.isdir (self.root):
            loggedos.system (logging.default_logger,
                             'mkdir -p %s' % self.root)
        
    def installed_files (self, package):
        return self._package_file_db[package].split ('\n')

    def is_installed (self, name):
        return self._package_file_db.has_key (name)

    def install_tarball (self, ball, name, prefix_dir):
        logging.action ('untarring: %(ball)s\n' % locals ())

        _z = misc.compression_flag (ball)
        _v = '' # self.os_interface.verbose_flag ()
        root = self.root
        lst = loggedos.read_pipe (logging.default_logger,
                                  'tar -t%(_z)s -f "%(ball)s"'
                                  % locals ()).split ('\n')
        conflicts = False
        for f in lst:
            if (self._file_package_db.has_key (f)
                and not os.path.isdir (self.root + '/' +  f)):
                logging.error ('already have file %s: %s\n' % (f, self._file_package_db[f]))
                conflicts = True

        if conflicts and not self.is_distro:
            raise Exception ('abort')

        loggedos.system (logging.default_logger,
                         'tar -C %(root)s -p -x%(_z)s%(_v)s -f %(ball)s'
                         % locals ())

        self._package_file_db[name] = '\n'.join (lst)
        for f in lst:
            # ignore directories.
            if not f.endswith ('/'):
                self._file_package_db[f] = name
            if f.endswith ('.la'):
                self.libtool_la_fixup (root, f)
            if f.endswith ('.pc'):
                self.pkgconfig_pc_fixup (root, f, prefix_dir)

    def libtool_la_fixup (self, root, file):
        # avoid using libs from build platform, by adding
        # %(system_root)s
        if file.startswith ('./'):
            file = file[2:]
        dir = os.path.dirname (file)
        loggedos.file_sub (logging.default_logger,
                           [('^libdir=.*',
                             """libdir='%(root)s/%(dir)s'""" % locals ()
                             ),],
                           '%(root)s/%(file)s' % locals (),
                           must_succeed=('tools/root' not in self.root
                                         and 'cross' not in dir))
        
    def pkgconfig_pc_fixup (self, root, file, prefix_dir):
        # avoid using libs from build platform, by adding
        # %(system_root)s
        if file.startswith ('./'):
            file = file[2:]
        dir = os.path.dirname (file)
        if '%' in prefix_dir or not prefix_dir:
            barf
        loggedos.file_sub (logging.default_logger,
                           [('(-I|-L) */usr',
                             '''\\1%(root)s%(prefix_dir)s''' % locals ()
                             ),],
                           '%(root)s/%(file)s' % locals ())

    def uninstall_package (self, name):
        logging.action ('uninstalling package: %s\n' % name)

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
                logging.verbose ('warning: %(d)s not empty\n' % locals ())
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
    def __init__ (self):
        self._packages = {}

        ## ugh mi 
        self.verbose = False
        
    def register_package_dict (self, d):
        nm = d['name']
        if d.has_key ('split_name'):
            nm = d['split_name']
        
        if 0 and (self._packages.has_key (nm)):
            if self._packages[nm]['spec_checksum'] != d['spec_checksum']:
                logging.info ('******** checksum of %s changed!\n\n' % nm)

            if self._packages[nm]['cross_checksum'] != d['cross_checksum']:
                logging.info ('******** checksum of cross changed for %s\n' % nm)
            return

        self._packages[nm] = d
   
        
    def register_package_header (self, package_hdr, branch_dict):
        if self.verbose:
            logging.info ('reading package header: %s\n'
                          % `package_hdr`)

        str = open (package_hdr).read ()

        d = dict (pickle.loads (str))

        if branch_dict.has_key (d['basename']):
            branch = branch_dict[d['basename']]
            if ':' in branch:
                (remote_branch, branch) = tuple (branch.split (':'))
            if branch != d['vc_branch']:
                suffix = d['vc_branch']
                logging.error ('ignoring header: %(package_hdr)s\n'
                               % locals ())
                logging.error ('package of branch: %(suffix)s, expecting: %(branch)s\n' % locals ())
                return
        elif d['vc_branch']:
            sys.stdout.write ('No branch for package %s, ignoring header: %s\n' % (d['basename'], package_hdr))
            return
        
        name = d['split_name']
        if 0:
          ## FIXME ?
          if self._package_dict_db.has_key (name):
              if str != self._package_dict_db[name]:
                  logging.info ("package header changed for %s\n" % name)

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
        #d = self._packages[name]
        d = self.package_dict (name)
        ball = '%(split_ball)s' % d
        hdr = '%(split_hdr)s' % d
        return os.path.exists (ball) and os.path.exists (hdr)

    def read_package_headers (self, s, branch_dict):
        if os.path.isdir (s) and not s.endswith ('/'):
            s += '/'
        for f in glob.glob ('%(s)s*hdr' % locals ()):
            self.register_package_header (f, branch_dict)


## FIXME: MI
class PackageManager (FileManager, PackageDictManager):
    """PackageManager is a FileManager, which also associates a
    key/value dict with each package.

    Such dicts come either from either 

    1. A build spec (ie. a python object)

    2. A pickled dict on disk, a package header

    3. 
    """

    
    def __init__ (self, root,  **kwargs):
        FileManager.__init__ (self, root, **kwargs)
        PackageDictManager.__init__ (self)
        
        dicts_db = self.config + '/dicts.db'
        self._package_dict_db = dbmodule.open (dicts_db, 'c')
        for k in self._package_dict_db.keys ():
            v = self._package_dict_db[k]
            self.register_package_dict (pickle.loads (v))

    def installed_package_dicts (self):
        names = self._package_file_db.keys ()
        return [self._packages[p] for p in names]

    def install_package (self, name):
        if self.is_installed (name):
            return
        logging.action ('installing package: %s\n' % name)
        if self._package_file_db.has_key (name):
            logging.error ('already have package: ' + name + '\n')
            raise Exception ('abort')
        d = self._packages[name]
        ball = '%(split_ball)s' % d
        self.install_tarball (ball, name, d['prefix_dir'])
        self._package_dict_db[name] = pickle.dumps (d)

    def uninstall_package (self, name):
        FileManager.uninstall_package (self, name)
        del self._package_dict_db[name]

    def source_name (self, name):
        return self._packages [name]['source_name']

    
class DependencyManager (PackageManager):

    """Manage packages that have dependencies and
    build_dependencies in their package dicts"""

    def __init__ (self, *args, **kwargs):
        PackageManager.__init__ (self, *args, **kwargs)
        self.include_build_deps = True

    def dependencies (self, name):
        assert type(name) == str
        try:
            return self.dict_dependencies (self._packages[name])
        except KeyError:
            logging.error ('no such package: %(name)s\n' % locals ())
            return list ()

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

        # 
        if not type (d) == type (todo):
            print type (d), '!=', type (todo)
            assert type (d) == type (todo)
        # New style class attempt...
        if (not ((isinstance (d, build.AutoBuild)
                  and isinstance (d, build.AutoBuild))
                 or (type (d) == type (todo)))):
            print type (d), '!=', type (todo)
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

def get_source_packages (settings, const_todo):
    """TODO is a list of (source) builds.

    Generate a list of AutoBuild needed to build TODO, in
    topological order
    """

    # Do not confuse caller, do not modify caller's todo
    todo = const_todo[:]
    todo += cross.get_build_dependencies (settings)

    spec_dict = dict ()
    sets = {settings.platform: settings}

    def with_platform (s, platform=settings.platform):
        return misc.with_platform (s, platform)

    def split_platform (u):
        return misc.split_platform (u, settings.platform)

    def name_to_dependencies_via_gub (url):
        platform, url = split_platform (url)
        if ':' in url:
            base, unused_parameters = misc.dissect_url (url)
            name = os.path.basename (base)
            ##DOCME or JUNKME
            ##name = re.sub ('\..*', '', name)
            key = url
        else:
            name = get_base_package_name (url)
            url = None
            key = name
            
        key = with_platform (key, platform)
        if spec_dict.has_key (key):
            spec = spec_dict[key]
        else:
            if not sets.has_key (platform):
                sets[platform] = gub.settings.Settings (platform)
            spec = dependency.Dependency (sets[platform], name, url).build ()
            spec_dict[key] = spec
            
        return map (get_base_package_name, spec.get_platform_build_dependencies ())

    def name_to_dependencies_via_distro (distro_packages, name):
        platform, name = split_platform (name)
        key = with_platform (name, platform)
        if spec_dict.has_key (key):
            spec = spec_dict[key]
        else:
            if name in todo or name not in distro_packages.keys ():
                if not sets.has_key (platform):
                    sets[platform] = gub.settings.Settings (platform)
                spec = dependency.Dependency (sets[platform], name).build ()
            else:
                spec = distro_packages[name]
            spec_dict[key] = spec
        return spec.get_platform_build_dependencies ()

    def name_to_dependencies_via_cygwin (name):
        return name_to_dependencies_via_distro (cygwin.get_packages (), name)

    def name_to_dependencies_via_debian (name):
        return name_to_dependencies_via_distro (debian.get_packages (), name)

    name_to_deps = name_to_dependencies_via_gub
    if settings.platform == 'cygwin':
        from gub import cygwin
        cygwin.init_dependency_resolver (settings)
        name_to_deps = name_to_dependencies_via_cygwin
    elif settings.platform.startswith ('debian'):
        from gub import debian
        debian.init_dependency_resolver (settings)
        name_to_deps = name_to_dependencies_via_debian

    topologically_sorted (todo, {}, name_to_deps)
    todo += cross.set_cross_dependencies (spec_dict)
    topologically_sorted (todo, {}, name_to_deps)

    # Fixup for build from url: spec_dict key is full url, change to
    # base name.  Must use list(dict.keys()), since dict changes during
    # iteration.
    for name in list (spec_dict.keys ()):
        spec = spec_dict[name]
        if name != spec.platform_name ():
            spec_dict[spec.platform_name ()] = spec

    if settings.is_distro:
        def obj_to_dependency_objects (obj):
            return [spec_dict[n] for n in obj.get_platform_build_dependencies ()]
    else:
        def obj_to_dependency_objects (obj):
            return [spec_dict[get_base_package_name (n)]
                    for n in obj.get_platform_build_dependencies ()]

    sorted_specs = topologically_sorted (spec_dict.values (), {},
                                         obj_to_dependency_objects)

    # Make sure we build dependencies in order
    sorted_names = [o.platform_name () for o in sorted_specs]
    dep_str = ' '.join (sorted_names).replace (with_platform (''), '')
    platform = settings.platform
    logging.info ('dependencies[%(platform)s]: %(dep_str)s\n' % locals ())
    return (sorted_names, spec_dict)
