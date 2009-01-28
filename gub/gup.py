# tools python has no gdbm, breaks simple home python/lilypond build
# but dbhash seems to break in odd ways:
#  File "bsddb/dbutils.py", line 62, in DeadlockWrap
#  DBPageNotFoundError: (-30987, 'DB_PAGE_NOTFOUND: Requested page not found')

import fcntl
import glob
import inspect
import os
import pickle
import re
import string
import sys

#
from gub import build
from gub import cross
from gub.db import db
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
        self._file_package_db = db.open (files_db, 'c')
        self._package_file_db = db.open (packages_db, 'c')
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
        
    def package_installed_files (self, name):
        return [file_name for file_name in self._package_file_db[name].decode ('utf8').split ('\n')]

    def installed_packages (self):
        return [name.decode ('utf8') for name in self._package_file_db.keys ()]

    def is_installed (self, name):
        return name in self.installed_packages ()

    def installed_files (self):
        return [file_name.decode ('utf8') for file_name in self._file_package_db.keys ()]

    def is_installed_file (self, name):
        return name in self.installed_files ()

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
            if (self.is_installed_file (f)
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

        lst = self.package_installed_files (name)

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
        if 'split_name' in d:
            nm = d['split_name']
        
        if 0 and (nm in self._packages):
            if self._packages[nm]['spec_checksum'] != d['spec_checksum']:
                logging.info ('******** checksum of %s changed!\n\n' % nm)

            if self._packages[nm]['cross_checksum'] != d['cross_checksum']:
                logging.info ('******** checksum of cross changed for %s\n' % nm)
            return

        self._packages[nm] = d
   
        
    def register_package_header (self, package_hdr, branch_dict):
        if self.verbose:
            logging.info ('reading package header: %s\n'
                          % package_hdr.__repr__ ())

        str = open (package_hdr).read ()
        header_name = os.path.basename (package_hdr)
        d = dict (pickle.loads (str))
        name = d['basename']
        vc_branch = d.get ('vc_branch', '')

        if name in branch_dict:
            branch = branch_dict[name]
            if ':' in branch:
                (remote_branch, branch) = tuple (branch.split (':'))
            if branch != vc_branch:
                logging.error ('package of branch: %(vc_branch)s, expecting: %(branch)s\n' % locals ())
                logging.error ('ignoring header: %(header_name)s\n' % locals ())
                return
        elif d['vc_branch']:
            logging.error ('no branch for package: %(name)s\n' % locals ())
            logging.error ('ignoring header: %(header_name)s\n' % locals ())
            logging.error ('available branch: %(vc_branch)s\n' % locals ())
            return
        
        name = d['split_name']
        if 0:
          ## FIXME ?
          if name in self._package_dict_db:
              if str != self._package_dict_db[name]:
                  logging.info ("package header changed for %s\n" % name)

              return

        self.register_package_dict (d)

    def unregister_package_dict (self, name):
        del self._packages[name]

    def is_registered (self, name):
        return name in self._packages

    def package_dict (self, name):
        return self._packages.get (name, dict ())

    def available_packages (self):
        return self._packages.keys ()

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
        self._package_dict_db = db.open (dicts_db, 'c')
        for k in self._package_dict_db.keys ():
            v = self._package_dict_db[k]
            self.register_package_dict (pickle.loads (v))

    def installed_package_dicts (self):
        return [self._packages[n] for n in self.installed_packages ()]

    def install_package (self, name):
        if self.is_installed (name):
            return
        logging.action ('installing package: %s\n' % name)
        if self.is_installed (name):
            logging.error ('already have package: ' + name + '\n')
            raise Exception ('abort')
        d = self._packages[name]
        ball = '%(split_ball)s' % d
        self.install_tarball (ball, name, d['prefix_dir'])
        self._package_dict_db[name] = pickle.dumps (d, protocol=2)

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
    if todo in done:
        return sorted

    done[todo] = 1

    def type_equal (a, b):
        return ((type (a) == type (b))
                or inspect.isclass (type (a)) == inspect.isclass (type (b)))

    deps = dependency_getter (todo)
    for d in deps:
        if recurse_stop_predicate and recurse_stop_predicate (d):
            continue
        if not type_equal (d, todo):
            print type (d), '!=', type (todo)
            print d.__class__, todo.__class__
            print d.__dict__, todo.__dict__
            print inspect.isclass (type (d)), inspect.isclass (type (todo))
            assert type_equal (a, b)
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

# FIXME: how to assign to outer var?
# FIXME: make this more plugin-ish
cygwin_resolver = None
debian_resolver = None

def get_source_packages (settings, const_todo):
    """TODO is a list of (source) builds.

    Generate a list of AutoBuild needed to build TODO, in
    topological order
    """

    # Do not confuse caller, do not modify caller's todo
    todo = const_todo[:]
    specs = dict ()
    sets = {settings.platform: settings}

    def with_platform (s, platform=settings.platform):
        return misc.with_platform (s, platform)

    def split_platform (u):
        return misc.split_platform (u, settings.platform)

    def name_to_dependencies_via_gub (url):
        platform, url = split_platform (url)
        if ':' in url:
            base, unused_parameters = misc.dissect_url (url)
            name = (os.path.basename (base)
                    .replace ('.git', ''))
            key = url
        else:
            name = get_base_package_name (url)
            url = None
            key = name
            
        key = with_platform (key, platform)
        if key in specs:
            spec = specs[key]
        else:
            if platform not in sets:
                sets[platform] = gub.settings.Settings (platform)
            spec = dependency.Dependency (sets[platform], name, url).build ()
            specs[key] = spec
            
        return map (get_base_package_name, spec.get_platform_build_dependencies ())

    def name_to_dependencies_via_distro (distro_packages, url):
        platform, url = split_platform (url)
        if ':' in url:
            base, unused_parameters = misc.dissect_url (url)
            name = (os.path.basename (base)
                    .replace ('.git', ''))
            key = url
        else:
            name = url #get_base_package_name (url)
            url = None
            key = name
            
        key = with_platform (key, platform)
        if key in specs:
            spec = specs[key]
        else:
            if name in todo or name not in distro_packages.keys ():
                if platform not in sets:
                    sets[platform] = gub.settings.Settings (platform)
                spec = dependency.Dependency (sets[platform], name).build ()
            else:
                spec = distro_packages[name]
            specs[key] = spec
        return spec.get_platform_build_dependencies ()

    # FIXME: how to assign to outer var?
    # cygwin_resolver = None
    def name_to_dependencies_via_cygwin (name):
        global cygwin_resolver #ugh
        if not cygwin_resolver:
            from gub import cygwin
            cygwin_resolver = cygwin.init_dependency_resolver (settings)
        return name_to_dependencies_via_distro (cygwin.get_packages (), name)

    #debian_resolver = None
    def name_to_dependencies_via_debian (name):
        global debian_resolver #ugh
        if not debian_resolver:
            from gub import debian
            debian_resolver = debian.init_dependency_resolver (settings)
        return name_to_dependencies_via_distro (debian.get_packages (), name)

    name_to_dependencies = {
        'cygwin': name_to_dependencies_via_cygwin,
        'debian': name_to_dependencies_via_debian,
        }

    def name_to_dependencies_broker (url):
        platform, x = split_platform (url)
        return name_to_dependencies.get (platform,
                                         name_to_dependencies_via_gub) (url)

    # Must iterate, try:
    #   bin/gub -p tools tar
    #   bin/gub -p tools make tar
    # or
    #   bin/gub darwin-ppc::libtool freebsd-64::libtool
    last_count = len (todo)
    while last_count != len (specs.keys ()):
        add = cross.set_cross_dependencies (specs)
        todo += [a for a in add if a not in todo]
        last_count = len (specs.keys ())
        topologically_sorted (todo, {}, name_to_dependencies_broker)

    # Fixup for build from url: specs key is full url, change to
    # base name.  Must use list(dict.keys()), since dict changes during
    # iteration.
    for name in list (specs.keys ()):
        spec = specs[name]
        if name != spec.platform_name ():
            specs[spec.platform_name ()] = spec

    if settings.is_distro:
        def obj_to_dependency_objects (obj):
            return [specs[n] for n in obj.get_platform_build_dependencies ()]
    else:
        def obj_to_dependency_objects (obj):
            return [specs[get_base_package_name (n)]
                    for n in obj.get_platform_build_dependencies ()]

    sorted_specs = topologically_sorted (specs.values (), {},
                                         obj_to_dependency_objects)

    # Make sure we build dependencies in order
    sorted_names = [o.platform_name () for o in sorted_specs]
    return (sorted_names, specs)
