import glob
import pickle
import os
import re
#
from gub import misc
from gub import repository
from gub import oslog
from gub.context import *

class PackageSpec:
    "How to package part of an install_root."
    
    def __init__ (self, os_interface):
        self._dict = {}
        self._os_interface = os_interface
        self._file_specs = []
        self._dependencies = []
        self._conflicts = []
        
    def set_dict (self, dict, sub_name):
        self._dict = dict.copy ()
        self._dict['sub_name'] = sub_name
        if sub_name:
            sub_name = '-' + sub_name
        s = ('%(name)s' % dict) + sub_name
        self._dict['split_name'] = s
        self._dict['split_ball'] = ('%(packages)s/%(split_name)s%(ball_suffix)s.%(platform)s.gup') % self._dict
        self._dict['split_hdr'] = ('%(packages)s/%(split_name)s%(vc_branch_suffix)s.%(platform)s.hdr') % self._dict
        self._dict['conflicts_string'] = ';'.join (self._conflicts)
        self._dict['dependencies_string'] = ';'.join (self._dependencies)
        self._dict['source_name'] = self.name ()
        if sub_name:
            self._dict['source_name'] = self.name ()[:-len (sub_name)]
        
    def expand (self, s):
        return s % self._dict
    
    def dump_header_file (self):
        hdr = self.expand ('%(split_hdr)s')
        self._os_interface.dump (pickle.dumps (self._dict), hdr)
        
    def clean (self):
        base = self.expand ('%(install_root)s')
        for f in self._file_specs:
            if f and f != '/' and f != '.':
                self._os_interface.system ('rm -rf %(base)s%(f)s ' % locals ())

    def create_tarball (self):
        path = os.path.normpath (self.expand ('%(install_root)s'))
        suffix = self.expand ('%(packaging_suffix_dir)s')
        split_ball = self.expand ('%(split_ball)s')
        self._os_interface._execute (oslog.PackageGlobs (path,
                                                         suffix,
                                                         self._file_specs,
                                                         split_ball))
    def dict (self):
        return self._dict

    def name (self):
        return '%(split_name)s' % self._dict
    
class BuildSpec (Os_context_wrapper):
    def __init__ (self, settings):
        Os_context_wrapper.__init__ (self, settings)

        self.verbose = settings.verbose
        self.settings = settings
        self.url = ''
        self.has_source = True
        self._dependencies = None
        self._build_dependencies = None
        
        self.spec_checksum = '0000' 
        self.cross_checksum = '0000'
        
        # TODO: move to PackageSpec, always instantiate.
        # then remove all if self.vc_repository checks
        self.vc_repository = None
        
        self.split_packages = []
        self.so_version = '1'

    def stages (self):
        return ['download', 'untar', 'patch',
                'configure', 'compile', 'install',
                'src_package', 'package', 'clean']

    @subst_method
    def LD_PRELOAD (self):
        return '%(gubdir)s/librestrict/librestrict.so'
    
    def get_substitution_dict (self, env={}):
        dict = {
            'CPATH': '',
            'CPLUS_INCLUDE_PATH': '',
            'C_INCLUDE_PATH': '',
            'LIBRARY_PATH': '/empty-means-cwd-in-feisty',
            }
        dict.update (env)
        d = Os_context_wrapper.get_substitution_dict (self, dict).copy ()
        return d
          
    def class_invoke_version (self, klas, name):
        name_version = name + '_' + self.version ().replace ('.', '_')
        if klas.__dict__.has_key (name_version):
            klas.__dict__[name_version] (self)

    def download (self):
        if self.vc_repository:
            self.vc_repository.download ()

    def get_repodir (self):
        return self.settings.downloads + '/' + self.name ()
    
    def get_conflict_dict (self):
        """subpackage -> list of confict dict."""
        return {'': [], 'devel': [], 'doc': [], 'runtime': []}
  
    def get_dependency_dict (self):
        """subpackage -> list of dependency dict."""
        # FIMXE: '' always depends on runtime?
        return {'': [], 'devel': [], 'doc': [], 'runtime': [], 'x11': []}
  
    def force_sequential_build (self):
        """Set to true if package can't handle make -jX """
        return False
    
    @subst_method
    def name (self):
        if 0: # old method, removes cross/
            file = self.__class__.__name__.lower ()
            file = re.sub ('__.*', '', file)
            file = re.sub ('_', '-', file)
        file = self.__class__.__module__

        ## UGH ? what happens if xx is in a normal name?!
        file = re.sub ('xx', '++', file)
        return file

    @subst_method
    def pretty_name (self):
        name = self.__class__.__name__
        name = re.sub ('__.*', '', name)
        return name
    
    @subst_method
    def file_name (self):
        if self.url:
            file = re.sub ('.*/([^/]+)', '\\1', self.url)
        else:
            file = os.path.basename (self.name ())
        return file

    @subst_method
    def source_checksum (self):
        if self.vc_repository:
            #return self.vc_repository.get_checksum ().replace ('/', '-')
            print 'FIXME: serialization: want checksum TOO SOON'
            return '0000'
        return self.version () 

    @subst_method
    def license_file (self):
        return '%(srcdir)s/COPYING'
    
    @subst_method
    def basename (self):
        return misc.ball_basename (self.file_name ())

    @subst_method
    def packaging_suffix_dir (self):
        return ''

    @subst_method
    def full_version (self):
        return self.version ()

    @subst_method
    def build_dependencies_string (self):
        deps = self.get_build_dependencies ()
        return ';'.join (deps)

    @subst_method
    def ball_suffix (self):
        # FIXME: use repository.version ()
        b = '-%(version)s'
        if self.vc_repository and self.vc_repository.is_tracking ():
            try:
                b = '-' + self.vc_repository.branch.replace ('/', '-')
            except AttributeError:
                pass
        return b

    @subst_method
    def vc_branch (self):
        b = ''
        if self.vc_repository and self.vc_repository.is_tracking ():
            try:
                b = self.vc_repository.branch.replace ('/', '-')
            except AttributeError:
                pass
        return b
    
    @subst_method
    def vc_branch_suffix (self):
        # FIXME: use repository.version ()
        b = ''
        if self.vc_repository and self.vc_repository.is_tracking ():
            try:
                b = '-' + self.vc_repository.branch.replace ('/', '-')
            except AttributeError:
                pass
        return b
        
    @subst_method
    def version (self):
        # kugh, must construct using vc_repository in __init__
        if not self.vc_repository :
            msg = 'need version, but repository not yet set: %s, type: %s class: %s' % (self.name (), type (self), self.__class__)
            raise Exception (msg)
        return self.vc_repository.version ()

    @subst_method
    def name_version (self):
        return '%s-%s' % (self.name (), self.version ())

    @subst_method
    def srcdir (self):
        return '%(allsrcdir)s/%(name)s%(ball_suffix)s'

    @subst_method
    def builddir (self):
        return '%(allbuilddir)s/%(name)s%(ball_suffix)s'

    @subst_method
    def install_root (self):
        return '%(installdir)s/%(name)s-%(version)s-root'

    @subst_method
    def install_prefix (self):
        return '%(install_root)s%(prefix_dir)s'

    @subst_method
    def install_command (self):
        return '''make %(makeflags)s DESTDIR=%(install_root)s install'''

    @subst_method 
    def configure_command (self):
        return '%(srcdir)s/configure --prefix=%(install_prefix)s'

    @subst_method
    def compile_command (self):
        return 'make %(makeflags)s '

    @subst_method
    def native_compile_command (self):
        c = 'make'

        job_spec = ' '
        if self.settings.native_distcc_hosts:
            job_spec = '-j%d ' % (2*len (self.settings.native_distcc_hosts.split (' ')))

            ## do this a little complicated: we don't want a trace of
            ## distcc during configure.
            c = 'DISTCC_HOSTS="%s" %s' % (self.settings.native_distcc_hosts, c)
            c = 'PATH="%(native_distcc_bindir)s:$PATH" ' + c
        elif (not self.force_sequential_build()
              and self.settings.cpu_count_str != '1'):
            job_spec += ' -j%s ' % self.settings.cpu_count_str

        c += job_spec
        return c


    @subst_method
    def src_package_ball (self):
        return '%(src_package_uploads)s/%(name)s%(ball_suffix)s-src.%(platform)s.tar.gz'

    @subst_method
    def src_package_uploads (self):
        return '%(packages)s'

    @subst_method
    def stamp_file (self):
        return '%(statusdir)s/%(name)s-%(version)s-%(source_checksum)s'

    @subst_method
    def rsync_command (self):
        return "rsync --exclude .git --exclude _darcs --exclude .svn --exclude CVS -v -a %(downloads)s/%(name)s-%(version)s/ %(srcdir)s"

    @subst_method
    def makeflags (self):
        return ''
    
    def get_stamp_file (self):
        stamp = self.expand ('%(stamp_file)s')
        return stamp

    def is_done (self, stage, stage_number):
        f = self.get_stamp_file ()
        if os.path.exists (f):
            return int (open (f).read ()) >= stage_number
        return False

    def set_done (self, stage, stage_number):
        self.dump ('%(stage_number)d' % locals (), self.get_stamp_file (), 'w')

    def autoupdate (self):
        self.os_interface._execute (oslog.AutogenMagic(self))

    def configure (self):
        self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command)s
''')

    def install_license (self):
        if self.expand ('%(license_file)s'):
            self.system ('mkdir -p %(install_root)s/license/', ignore_errors=True)
            self.system ('cp %(license_file)s %(install_root)s/license/%(name)s')

    def broken_install_command (self):
        """For packages that do not honor DESTDIR.
        """

        # FIXME: use sysconfdir=%(install_PREFIX)s/etc?  If
        # so, must also ./configure that way
        return misc.join_lines ('''make %(makeflags)s install
bindir=%(install_prefix)s/bin
aclocaldir=%(install_prefix)s/share/aclocal
datadir=%(install_prefix)s/share
exec_prefix=%(install_prefix)s
gcc_tooldir=%(install_prefix)s
includedir=%(install_prefix)s/include
infodir=%(install_prefix)s/share/info
libdir=%(install_prefix)s/lib
libexecdir=%(install_prefix)s/lib
mandir=%(install_prefix)s/share/man
prefix=%(install_prefix)s
sysconfdir=%(install_prefix)s/etc
tooldir=%(install_prefix)s
''')

    def kill_libtool_installation_test (self, file):
        self.file_sub ([(r'if test "\$inst_prefix_dir" = "\$destdir"; then',
                         'if false && test "$inst_prefix_dir" = "$destdir"; then')],
                       file, must_succeed=True)
        
    def update_libtool (self):
        def update (file):
            new = self.expand ('%(system_prefix)s/bin/libtool')
            if not os.path.exists (new):
                self.error ('Cannot update libtool: no such file: %(new)s' % locals ())
                raise Exception ('barf')
            self.system ('cp %(new)s %(file)s', locals ())
            self.kill_libtool_installation_test (file)
            self.system ('chmod 755  %(file)s', locals ())
        self.map_locate (update, '%(builddir)s', 'libtool')

    def install (self):
        self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
rm -f %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/share/info/dir %(install_root)s%(packaging_suffix_dir)s/%(prefix_dir)s/cross/info/dir %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/info/dir
''')
        self.install_license ()
        self.libtool_installed_la_fixups ()

    def libtool_installed_la_fixups (self):
        def installed_la_fixup (la):
            (dir, base) = os.path.split (la)
            base = base[3:-3]
            dir = re.sub (r"^\./", "/", dir)
            self.file_sub ([(''' *-L *[^\"\' ][^\"\' ]*''', ''),
                    ('''( |=|\')(/[^ ]*usr/lib|%(targetdir)s.*)/lib([^ \'/]*)\.(a|la|so)[^ \']*''',
                    '\\1-l\\3 '),
                    ('^old_library=.*',
                    """old_library='lib%(base)s.a'"""),
                    ],
                   la, env=locals ())
            if self.settings.platform.startswith ('mingw'):
                self.file_sub ([('library_names=.*',
                                 "library_names='lib%(base)s.dll.a'")],
                               la, env=locals ())
        self.map_locate (installed_la_fixup, '%(install_root)s', 'lib*.la')

    def compile (self):
        self.system ('cd %(builddir)s && %(compile_command)s')

    # FIXME: should not misuse patch for auto stuff
    def patch (self):
        self.autoupdate ()

    @subst_method
    def is_sdk_package (self):
        return 'false'

    def rewire_symlinks (self):
        def rewire (file):
            if os.path.islink (file):
                s = os.readlink (file)
                if s.startswith ('/') and self.settings.system_root not in s:
                    new_dest = os.path.join (self.settings.system_root, s[1:])
                    os.remove (file)
                    self.os_interface.action ('changing absolute link %(file)s -> %(new_dest)s' % locals())
                    os.symlink (new_dest, file)
        self.map_locate (rewire, '%(install_root)s', '*')

    def package (self):
        self.rewire_symlinks ()
        ps = self.get_packages ()
        for p in ps:
            p.create_tarball ()
            p.dump_header_file ()
            p.clean ()
        self.system ('rm -rf %(install_root)s')
        
    def get_build_dependencies (self):
        return []

    def get_subpackage_definitions (self):
	prefix_dir = self.settings.prefix_dir
        d = {
            'base': [prefix_dir + '/share'],
            'common': [prefix_dir + '/share'],
            'devel': [
            prefix_dir + '/bin/*-config',
            prefix_dir + '/include',
            prefix_dir + '/cross/bin',
            prefix_dir + '/cross/include',
            prefix_dir + '/cross/lib',
            prefix_dir + '/cross/libexec',
            prefix_dir + '/cross/' + self.settings.target_architecture,
            prefix_dir + '/share/aclocal',
            prefix_dir + '/lib/lib*.a',
            prefix_dir + '/lib/pkgconfig',
            ],
            'doc': [
            prefix_dir + '/share/doc',
            prefix_dir + '/share/gtk-doc',
            prefix_dir + '/share/info',
            prefix_dir + '/share/man',
            prefix_dir + '/cross/info',
            prefix_dir + '/cross/man',
            ],
            'runtime': ['/lib', prefix_dir + '/lib', prefix_dir + '/share'],
            'x11': [prefix_dir + '/X11', prefix_dir + '/X11R6'],
            '' : ['/'],
            }
        return d
    
    def get_subpackage_names (self):
        return ['devel', 'doc', '']

    ## FIXME: when only patched in via MethodOverride, the real descr_dict,
    ## category_dict are not pickled and cygwin packaging fails
    def description_dict (self):
        return {}
    def category_dict (self):
        return {}

    def get_packages (self):
        defs = dict (self.get_subpackage_definitions ())

        ps = []

        conflict_dict = self.get_conflict_dict ()
        dep_dict = self.get_dependency_dict ()
        descr_dict = self.description_dict ()
        category_dict = self.category_dict ()
        
        for sub in self.get_subpackage_names ():
            filespecs = defs[sub]
            
            p = PackageSpec (self.os_interface)

            p._file_specs = filespecs
            p.set_dict (self.get_substitution_dict (), sub)

            conflict_str = ';'.join (conflict_dict.get (sub, []))
            if p._dict.has_key ('conflicts_string'):
                conflict_str = p._dict['conflicts_string'] + ';' + conflict_str
            p._dict['conflicts_string'] = conflict_str

            dep_str = ';'.join (dep_dict.get (sub, []))
            if p._dict.has_key ('dependencies_string'):
                dep_str = p._dict['dependencies_string'] + ';' + dep_str
            p._dict['dependencies_string'] = dep_str

	    ## FIXME make generic: use cross.get_subpackage_dict_methods () or similar.
            desc_str = descr_dict.get (sub, '')
            p._dict['description'] = desc_str

            cat_str = category_dict.get (sub, '')
            p._dict['category'] = cat_str
            
            ps.append (p)

        return ps
    
    def src_package (self):
        # URG: basename may not be source dir name, eg,
        # package libjpeg uses jpeg-6b.  Better fix at untar
        # stage?
        dir_name = re.sub (self.expand ('%(allsrcdir)s/'), '',
                           self.expand ('%(srcdir)s'))
        _v = self.verbose_flag ()
        self.system ('''
tar -C %(allsrcdir)s --exclude "*~" --exclude "*.orig"%(_v)s -zcf %(src_package_ball)s %(dir_name)s
''',
                     locals ())

    def clean (self):
        self.system ('rm -rf  %(stamp_file)s %(install_root)s', locals ())
        if self.vc_repository and self.vc_repository.is_tracking ():
            return

        self.system ('''rm -rf %(srcdir)s %(builddir)s''', locals ())

    def untar (self):
        if not self.has_source:
            return False
        if not (self.vc_repository and self.vc_repository.is_tracking ()) :
            self.system ('rm -rf %(srcdir)s %(builddir)s %(install_root)s')

        if self.vc_repository:
            self.vc_repository.update_workdir (self.expand ('%(srcdir)s'))
            
        if (os.path.isdir (self.expand ('%(srcdir)s'))):
            self.system ('chmod -R +w %(srcdir)s', ignore_errors=True)

    def pre_install_smurf_exe (self):
        for i in self.locate_files ('%(builddir)s', '*.exe'):
            base = os.path.splitext (i)[0]
            self.system ('''mv %(i)s %(base)s''', locals ())

    def post_install_smurf_exe (self):
        for i in (self.locate_files ('%(install_root)s/bin', '*')
                  + self.locate_files ('%(install_prefix)s/bin', '*')):
            if (not os.path.islink (i)
                and not os.path.splitext (i)[1]
                and self.read_pipe ('file -b %(i)s', locals ()).startswith ('MS-DOS executable PE')):
                self.system ('''mv %(i)s %(i)s.exe''', locals ())

    def install_readmes (self):
        self.system ('''
mkdir -p %(install_prefix)s/share/doc/%(name)s
''')
        def copy_readme (file):
            if (os.path.isfile (file)
                and not os.path.basename (file).startswith ('Makefile')
                and not os.path.basename (file).startswith ('GNUmakefile')):
                self.copy (file, '%(install_prefix)s/share/doc/%(name)s')
        self.map_locate (copy_readme, '%(srcdir)s', '[A-Z]*')

    def build_version (self):
        "the version in the shipped package."
        # FIXME: ugly workaround needed for lilypond package...
        return '%(version)s'

    def build_number (self):
        # FIXME: actually need the packages' build number here...
        build_number_file = '%(gubdir)s/buildnumber-%(lilypond_branch)s.make'
        d = misc.grok_sh_variables (self.expand (build_number_file))
        b = '%(INSTALLER_BUILD)s' % d
        return b

    # TODO: junk this, always set repo in __init__
    def with_vc (self, repo):
        self.vc_repository = repo
        self.vc_repository.set_oslog (self.os_interface)
        return self

    def with_tarball (self, mirror='', version='', format='gz', strip_components=1, name=''):
        return self.with_vc (self.get_tarball (mirror, version, format, strip_components, name))

    def get_tarball (self, mirror, version, format='gz', strip_components=1, name=''):
        if not name:
            name = os.path.basename (self.name ())
        if not format:
            format = self.__dict__.get ('format', 'gz')
        if not mirror:
            mirror = self.__dict__.get ('url', '')
        if not version and self.version:
            version = self.ball_version

        from gub import repository
        return repository.NewTarBall (self.settings.downloads, mirror, name, version, format, strip_components)


    # TODO: junk this, use TarBall ()or Version ()
    def with_template (self,
              mirror='',
              version='',
              strip_components=1,
              format='',
              name=''):

        if not name:
            name = os.path.basename (self.name ())
        if not format:
            format = self.__dict__.get ('format', 'gz')
        if not mirror:
            mirror = self.__dict__.get ('url', '')
        if not version and self.version:
            version = self.ball_version
        if not version and self.vc_repository:
            version = self.vc_repository.version ()

        self.format = format
        self.ball_version = version
        self.url = mirror

        ball_version = version
        package_arch = self.settings.package_arch
        if mirror:
            repo = repository.TarBall (self.settings.downloads,
                                       # Hmm, better to construct
                                       # mirror later?
                                       mirror % locals (),
                                       version,
                                       strip_components=strip_components)
        else:
            repo = repository.Version (version)

        return self.with_vc (repo)

class BinarySpec (BuildSpec):
    def configure (self):
        pass

    def patch (self):
        pass

    def compile (self):
        pass

    def install (self):
        
        """Install package into %(install_root). Any overrides should
        follow this command, since it will erase the old install_root first."""
        
        self.system ('mkdir -p %(install_root)s')

        _v = self.os_interface.verbose_flag ()
        self.system ('tar -C %(srcdir)s -cf- . | tar -C %(install_root)s%(_v)s -p -xf-', env=locals ())
        self.libtool_installed_la_fixups ()

    def get_subpackage_names (self):
        # FIXME: splitting makes that cygwin's gettext + -devel subpackage
        # gets overwritten by cygwin's gettext-devel + '' base package
        return ['']

    # FIXME: no src packages for binary specs
    # They used to work, but now they fail?
    def src_package (self):
        pass

class NullBuildSpec (BuildSpec):
    """Placeholder for downloads """

    def compile (self):
        pass
    def configure (self):
        pass
    def install (self):
        self.system ('mkdir -p %(install_root)s')
    def untar (self):
        pass
    def patch (self):
        pass
    def src_package (self):
        pass

class SdkBuildSpec (NullBuildSpec):
    def untar (self):
        BuildSpec.untar (self)

    def get_subpackage_names (self):
        return ['']
    
    ## UGH: should store superclass names of each package.
    def is_sdk_package (self):
        return 'true'
    
    def install_root (self):
        return self.srcdir ()

class Change_target_dict:
    def __init__ (self, package, override):
        self._target_dict_method = package.get_substitution_dict
        self._add_dict = override

    def target_dict (self, env={}):
        env_copy = env.copy ()
        env_copy.update (self._add_dict)
        d = self._target_dict_method (env_copy)
        return d

    def append_dict (self, env={}):
        d = self._target_dict_method ()
        for (k,v) in self._add_dict.items ():
            d[k] += v

        d.update (env)
        d = recurse_substitutions (d)
        return d

def change_target_dict (package, add_dict):
    """Override the get_substitution_dict() method of PACKAGE."""
    try:
        package.get_substitution_dict = Change_target_dict (package, add_dict).target_dict
    except AttributeError:
        pass

def append_target_dict (package, add_dict):
    """Override the get_substitution_dict() method of PACKAGE."""
    try:
        package.get_substitution_dict = Change_target_dict (package, add_dict).append_dict
    except AttributeError:
        pass

def get_class_from_spec_file (settings, file_name, name):
    import misc
    settings.os_interface.info ('reading spec: ' + file_name + '\n')
    module = misc.load_module (file_name, name)

    # cross/gcc.py:Gcc will be called: cross/Gcc.py,
    # to distinguish from specs/gcc.py:Gcc.py
    base = os.path.basename (name)
    class_name = ((base[0].upper () + base[1:])
                  .replace ('-', '_')
                  .replace ('+', 'x'))
    full = class_name + '__' + settings.platform.replace ('-', '__')

    d = module.__dict__
    klass = None
    while full:
        if d.has_key (full):
            klass = d[full]
            break
        full = full[:max (full.rfind ('__'), 0)]

#    dropped feature:
#    version = xxx at toplevel of spec file
#    mirror = xxx at toplevel of spec file
#    for i in init_vars.keys ():
#        if d.has_key (i):
#            init_vars[i] = d[i]

    return klass

def get_build_spec (flavour, settings, url):
    """
    Return BuildSpec instance to build package from URL.

    URL can be partly specified (eg: only a name, `lilypond'),
    defaults are taken from the spec file.
    """
    name = url
    if url.find (':') >= 0:
        name = os.path.basename (url)

    klass = None
    checksum = '0000'
    file_base = name + '.py'
    for dir in (settings.specdir + '/' + settings.platform,
                settings.specdir + '/' + settings.os,
                settings.specdir):
        file_name = dir + '/' + file_base
        if os.path.exists (file_name):
            if not klass:
                klass = get_class_from_spec_file (settings, file_name, name)
            import md5
            # FIXME: pretty lame, checksum based on all matching
            # specs found, eg
            # linux-x86/cross/binutils, linux/cross/binutils, cross/binutils
            checksum += md5.md5 (open (file_name).read ()).hexdigest ()

    repo = None
    if not klass:
        if misc.is_ball (name):
            ball = name
            name, version_tuple, format = misc.split_ball (ball)
        elif name.find ('/') >= 0:
            name = os.path.basename (name)
        settings.os_interface.error ('NO SPEC for package: %(name)s\n'
                                     % locals ())
        from new import classobj
        # Direct url build feature
        #   * gub http://ftp.gnu.org/pub/gnu/tar/tar-1.18.tar.gz
        # WIP:
        #   * gub git://git.kernel.org/pub/scm/git/git
        #   * gub bzr:http://bazaar.launchpad.net/~yaffut/yaffut/yaffut.bzr
        # must remove specs/git.py for now to get this to work.
        # git.py overrides repository and branch settings

        ### building for local without spec hack
        if settings.platform == 'local':
            from gub import toolpackage
            flavour = toolpackage.ToolBuildSpec

        klass = classobj (name, (flavour,), {})
        klass.__module__ = name
        try:
           dir = os.path.join (settings.downloads, name)
           repo = repository.get_repository_proxy (dir, url, '', '')
        except repository.UnknownVcSystem:
            # FIXME: remove this or needed for distro builds: debian/cygwin?
            pass
    package = klass (settings)
    package.spec_checksum = checksum
    from gub import cross
    package.cross_checksum = cross.get_cross_checksum (settings.platform)
    if repo:
        package.with_vc (repo)

    return package
