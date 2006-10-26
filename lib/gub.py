# own
import cvs
import download
import glob
import misc
import locker
import repository
import gitrepo

# sys
import pickle
import os
import re
import string
import subprocess
import sys
import md5

from context import *

class PackageSpec:
    "How to package part of an install_root."
    
    def __init__ (self, os_interface):
        self._dict = {}
        self._os_interface = os_interface
        self._file_specs = []
        self._dependencies = []
        
    def set_dict (self, dict, sub_name):
        self._dict = dict.copy ()
        self._dict['sub_name'] = sub_name
        
        if sub_name:
            sub_name = '-' + sub_name

        s = ('%(name)s' % dict) + sub_name

        self._dict['split_name'] = s

        suffix = '%(verson)s'
        if dict['vc_branch_suffix']:
           suffix = dict['vc_branch_suffix']
            
        self._dict['split_ball'] = '%(gub_uploads)s/%(split_name)s-' + suffix +'.%(platform)s.gup' % self._dict
        self._dict['split_hdr'] = '%(gub_uploads)s/%(split_name)s%(vc_branch_suffix)s.%(platform)s.hdr' % self._dict

        deps =  ';'.join (self._dependencies)
        self._dict['dependencies_string'] = deps
        
    def expand (self, s):
        return s % self._dict
    
    def dump_header_file (self):
        hdr = self.expand ('%(split_hdr)s' )
        self._os_interface.dump (pickle.dumps (self._dict), hdr)
        
    def clean (self):
        for f in self._file_specs:
            base = self.expand ('rm -rf %(install_root)s/')
            self._os_interface.system (base + f)
            
    def create_tarball (self):
        cmd = 'tar -C %(install_root)s/%(packaging_suffix_dir)s --ignore-failed --exclude="*~" -zcf %(split_ball)s '
        cmd += (' '.join ('$(cd %%(install_root)s && echo ./%s)'
                          % f for f in self._file_specs)).replace ('//','/')
        cmd = self.expand (cmd)
        self._os_interface.system (cmd)

    def dict (self):
        return self._dict

    def name (self):
        return "%(split_name)s" % self._dict
    
class BuildSpec (Os_context_wrapper):
    def __init__ (self, settings):
        Os_context_wrapper.__init__(self, settings)

        self.verbose = settings.verbose ()
        self.settings = settings
        self.url = ''
        self.has_source = True
        self._dependencies = None
        self._build_dependencies = None
        
        self.spec_checksum = '0000' 
        self.cross_checksum = '0000'
        
        self.vc_repository = None
        
        self.split_packages = []
        self.so_version = '1'

    # urg: naming conflicts with module.
    def do_download (self):
        if self.vc_repository:
            self.vc_download ()
        else:
            self.wget ()

    def get_repodir (self):
        return self.settings.downloads + '/' + self.name ()
    def get_dependency_dict (self):
        """subpackage -> list of dependency dict."""
        
        # FIMXE: '' always depends on runtime?
        return {'': [], 'devel': [], 'doc': [], 'runtime': []}
  
    def broken_for_distcc (self):
        """Set to true if package can't handle make -jX """
        return False
    
    def is_downloaded (self):
        if not self.has_source:
            return True
        
        name = self.expand ('%(downloads)s/%(file_name)s')
        return os.path.exists (name)

    def wget (self):
        if not self.is_downloaded ():
            misc.download_url (self.expand (self.url), self.expand ('%(downloads)s'))

    def vc_download (self):
        self.vc_repository.download ()
        return

    @subst_method
    def name (self):
        file = self.__class__.__name__.lower ()
        file = re.sub ('__.*', '', file)
        file = re.sub ('_', '-', file)

        ## UGH ? what happens if xx is in a normal name?!
        file = re.sub ('xx', '++', file)
        return file

    @subst_method
    def file_name (self):
        file = re.sub ('.*/([^/]+)', '\\1', self.url)
        return file

    

    @subst_method
    def source_checksum (self):
        if self.vc_repository:
            return self.vc_repository.get_checksum ()
        
        return self.version () 

    @subst_method
    def license_file (self):
        return '%(srcdir)s/COPYING'
    
    @subst_method
    def basename (self):
        f = self.file_name ()
        f = re.sub ('.tgz', '', f)
        f = re.sub ('-src\.tar.*', '', f)
        f = re.sub ('\.tar.*', '', f)
        f = re.sub ('_%\(package_arch\)s.*', '', f)
        f = re.sub ('_%\(version\)s', '-%(version)s', f)
        return f

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
    def vc_branch_suffix (self):
        b = ''
        if self.vc_repository and self.vc_repository.is_tracking ():
            try:
                b = self.vc_repository.branch
            except AttributeError:
                pass
        return b
        
    @subst_method
    def version (self):
        return misc.split_version (self.ball_version)[0]

    @subst_method
    def name_version (self):
        return '%s-%s' % (self.name (), self.version ())

    @subst_method
    def srcdir (self):
        if self.vc_branch_suffix ():
            return '%(allsrcdir)s/%(name)s-%(vc_branch_suffix)s'
        else:
            return self.settings.allsrcdir + '/' + self.basename ()

    @subst_method
    def builddir (self):
        if self.vc_branch_suffix ():
            return '%(allsrcdir)s/%(name)s-%(vc_branch_suffix)s'
        else:
            return self.settings.allbuilddir + '/' + self.basename ()

    @subst_method
    def install_root (self):
        return '%(installdir)s/%(name)s-%(version)s-root'

    @subst_method
    def install_prefix (self):
        return self.install_root () + '/usr'

    @subst_method
    def install_command (self):
        return '''make DESTDIR=%(install_root)s install'''

    @subst_method
    def configure_command (self):
        return '%(srcdir)s/configure --prefix=%(install_prefix)s'

    @subst_method
    def compile_command (self):
        return 'make'

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
        elif self.settings.cpu_count_str <> '1':
            job_spec += ' -j%s ' % self.settings.cpu_count_str

        c += job_spec
        return c


    @subst_method
    def src_package_ball (self):
        return '%(src_package_uploads)s/%(name)s-%(version)s-src.%(platform)s.tar.gz'

    @subst_method
    def src_package_uploads (self):
        return '%(gub_uploads)s'

    @subst_method
    def stamp_file (self):
        return '%(statusdir)s/%(name)s-%(version)s'

    @subst_method
    def rsync_command (self):
        return "rsync --exclude .git --exclude _darcs --exclude .svn --exclude CVS -v -a %(downloads)s/%(name)s-%(version)s/ %(srcdir)s"

    def get_stamp_file (self):
        stamp = self.expand ('%(stamp_file)s')
        return stamp

    def is_done (self, stage, stage_number):
        f = self.get_stamp_file ()
        if os.path.exists (f):
            return int (open (f).read ()) >= stage_number
        return False

    def set_done (self, stage, stage_number):
        open (self.get_stamp_file (),'w'). write ('%d' % stage_number) 

    def autoupdate (self, autodir=0):
        if not autodir:
            autodir = self.srcdir ()
        if os.path.isdir (os.path.join (self.srcdir (), 'ltdl')):
            self.system ('''
rm -rf %(autodir)s/libltdl
cd %(autodir)s && libtoolize --force --copy --automake --ltdl
''', locals ())
        else:
            self.system ('''
cd %(autodir)s && libtoolize --force --copy --automake
''', locals ())
        if os.path.exists (os.path.join (autodir, 'bootstrap')):
            self.system ('''
cd %(autodir)s && ./bootstrap
''', locals ())
        elif os.path.exists (os.path.join (autodir, 'autogen.sh')):

            ## --noconfigure ??
            ## is --noconfigure standard for autogen? 
            self.system ('''
cd %(autodir)s && bash autogen.sh  --noconfigure
''', locals ())
        else:
            self.system ('''
cd %(autodir)s && aclocal -I %(system_root)s/usr/share/aclocal
cd %(autodir)s && autoheader -I %(system_root)s/usr/share/aclocal
cd %(autodir)s && autoconf -I %(system_root)s/usr/share/aclocal
''', locals ())
            if os.path.exists (self.expand ('%(srcdir)s/Makefile.am')):
                self.system ('''
cd %(srcdir)s && automake --add-missing --foreign
''', locals ())


    def configure (self):
        self.system ('''
mkdir -p %(builddir)s
cd %(builddir)s && %(configure_command)s
''')

    def install_license (self):
        if self.expand ('%(license_file)s'):
            self.system ('mkdir -p %(install_root)s/license/', ignore_error=True)
            self.system ('cp %(license_file)s %(install_root)s/license/%(name)s')
        
    def broken_install_command (self):
        """For packages that do not honor DESTDIR.
        """

        # FIXME: use sysconfdir=%(install_PREFIX)s/etc?  If
        # so, must also ./configure that way
        return misc.join_lines ('''make install
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
        lst = self.locate_files ('%(builddir)s', 'libtool')
        if lst:
            new = self.expand ('%(system_root)s/usr/bin/libtool')
            if not os.path.exists (new):
                self.log_command ("Cannot update libtool: no such file: %(new)s" % locals ())
                raise 'barf'
            for i in lst:
                self.system ('cp %(new)s %(i)s', locals ())
                self.kill_libtool_installation_test (i)
                self.system ('chmod 755  %(i)s', locals ())

    def install (self):
        self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
rm -f %(install_root)s/%(packaging_suffix_dir)s/usr/share/info/dir %(install_root)s/%(packaging_suffix_dir)s/usr/cross/info/dir %(install_root)s/%(packaging_suffix_dir)s/usr/info/dir
''')
        self.install_license ()
        self.libtool_installed_la_fixups ()

    def libtool_installed_la_fixups (self):
        for la in misc.find (self.expand ('%(install_root)s'), '\.la$'):
            (dir, base) = os.path.split (la)
            base = base[3:-3]
            dir = re.sub (r"^\./", "/", dir)
            full_la = self.expand ("%(install_root)s/%(la)s", locals())

            self.file_sub ([(''' *-L *[^\"\' ][^\"\' ]*''', ''),
                    ('''( |=|\')(/[^ ]*usr/lib|%(targetdir)s.*)/lib([^ \'/]*)\.(a|la|so)[^ \']*''',
                    '\\1-l\\3 '),
                    ('^old_library=.*',
                    """old_library='lib%(base)s.a'"""),
                    ],
                   full_la, env=locals ())
            if self.settings.platform.startswith ('mingw'):
                self.file_sub ([('library_names=.*',
                                 "library_names='lib%(base)s.dll.a'")],
                               full_la, env=locals())

            # avoid using libs from build platform, by adding %(system_root)s
            self.file_sub ([('^libdir=.*',
                             """libdir='%(system_root)s/%(dir)s'"""),
                            ],
                           full_la, env=locals ())

    def compile (self):
        self.system ('cd %(builddir)s && %(compile_command)s')

    # FIXME: should not misusde patch for auto stuff
    def patch (self):
        if not os.path.exists ('%(srcdir)s/configure' \
                   % self.get_substitution_dict ()):
            self.autoupdate ()

    @subst_method
    def is_sdk_package (self):
        return 'false'
    
    def package (self):
        ps = self.get_packages ()
        for p in ps:
            p.create_tarball ()
            p.dump_header_file ()
            p.clean ()
            
    def get_build_dependencies (self):
        return []

    def get_subpackage_definitions (self):
        d ={
            'devel': [
            '/usr/bin/*-config',
            '/usr/include',
            '/usr/cross/include',
            '/usr/share/aclocal',
            '/usr/lib/lib*.a',
            '/usr/lib/pkgconfig',
            ],
            'doc': [
            '/usr/share/doc',
            '/usr/share/gtk-doc',
            '/usr/share/info',
            '/usr/share/man',
            '/usr/cross/info',
            '/usr/cross/man',
            ],
            'runtime': ['/usr/lib', '/usr/share'],
            '' : ['/'],
            }
        return d
    
    def get_subpackage_names (self):
        return ['devel', 'doc', '']

    ## FIXME: patch in via MethodOverride
    def description_dict (self):
        return {}

    ## FIXME: patch in via MethodOverride
    def category_dict (self):
        return {'': 'interpreters',
                'runtime': 'libs',
                'devel': 'devel libs',
                'doc': 'doc'}
    
    def get_packages (self):
        defs = dict (self.get_subpackage_definitions ())

        ps = []

        dep_dict = self.get_dependency_dict ()
        descr_dict = self.description_dict  ()
        category_dict = self.description_dict  ()
        
        for sub in self.get_subpackage_names ():
            filespecs = defs[sub]
            
            p = PackageSpec (self.os_interface)
            if sub:
                p._dependencies = [self.expand ("%(name)s")]

            p._file_specs = filespecs
            p.set_dict (self.get_substitution_dict (), sub)

            dep_str = ';'.join (dep_dict.get (sub, []))
            if p._dict.has_key ('dependencies_string'):
                dep_str =  p._dict['dependencies_string'] + ';' + dep_str


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
        self.system ('''
tar -C %(allsrcdir)s --exclude "*~" --exclude "*.orig"  -zcf %(src_package_ball)s %(dir_name)s
''',
                     locals ())

    def clean (self):
        self.system ('rm -rf  %(stamp_file)s %(install_root)s', locals ())
        if self.vc_repository and self.vc_repository.is_tracking ():
            return

        self.system ('''rm -rf %(srcdir)s %(builddir)s''', locals ())

    def _untar (self, dir):
        tarball = self.expand("%(downloads)s/%(file_name)s")
        if not os.path.exists (tarball):
            raise 'no such file: ' + tarball
        if self.format == 'deb':
            self.system ('''
mkdir -p %(srcdir)s
ar p %(tarball)s data.tar.gz | tar -C %(dir)s -zxf-
''',
                  locals ())
        else:
            flags = download.untar_flags (tarball)
            self.system ('''
tar -C %(dir)s %(flags)s %(tarball)s
''',
                  locals ())

    def untar (self):
        if not self.has_source:
            return False
        if self.vc_repository:
            self.vc_repository.update_workdir (self.expand ('%(srcdir)s'))
            
        else:
            self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
''')
            self._untar ('%(allsrcdir)s')

        if (os.path.isdir (self.expand ('%(srcdir)s'))):
            self.system ('cd %(srcdir)s && chmod -R +w .')

    def untar_cygwin_src_package_variant2 (self, file_name, split=False):
        '''Unpack this unbelievably broken version of Cygwin source packages.

foo[version][-split]-x.y.z-b.tar.bz2 contains
foo[-split]-x.y.z.tar.[bz2|gz] and foo[version]-x.y.z-b.patch
(and optionally foo[version]-x.y.z-b.patch2 ...).
foo-x.y.z.tar.[bz2|gz] contains foo-x.y.z.  The patch contains patches
against all foo split source balls, so applying it may fail partly and
complain about missing files.'''
        
        file_name = self.expand (file_name)
        import misc
        t = misc.split_ball (file_name)
        print 'split: ' + `t`
        no_src = re.sub ('-src', '', file_name)
        base = re.sub ('\.tar\..*', '', no_src)
        # FIXME: use split iso custom ball_re macramee
        ball_re = '^([a-z]+)([.0-9]+)?(-[a-z+]+)?(.*)(-[0-9]+)'
        m = re.match (ball_re, base)
        if m.group (3):
            second_tarball = re.sub (ball_re, '\\1\\3\\4', base)
        else:
            second_tarball = re.sub (ball_re, '\\1\\4', base)
        print 'second_tarball: ' + second_tarball
        if split and m.group (3):
            second_tarball_contents = re.sub (ball_re, '\\1\\3\\4', base)
        else:
            second_tarball_contents = re.sub (ball_re, '\\1\\4', base)
        print 'second_tarball_contents: ' + second_tarball_contents
        flags = '-jxf'
        self.system ('''
rm -rf %(allsrcdir)s/%(base)s
tar -C %(allsrcdir)s %(flags)s %(downloads)s/%(file_name)s
''',
                     locals ())
        tgz = 'tar.bz2'
        if not os.path.exists (self.expand ('%s(allsrcdir)s/%(second_tarball)s.%(tgz)s',
                                            locals ())):
            flags = '-zxf'
            tgz = 'tar.gz'
        self.system ('''
tar -C %(allsrcdir)s %(flags)s %(allsrcdir)s/%(second_tarball)s.%(tgz)s
''',
                     locals ())
        if split:
            return
        if m.group (2):
            patch = re.sub (ball_re, '\\1\\2\\4\\5.patch', base)
        else:
            patch = re.sub (ball_re, '\\1\\4\\5.patch', base)
        print 'patch: ' + patch
        self.system ('''
cd %(allsrcdir)s && mv %(second_tarball_contents)s %(base)s
cd %(srcdir)s && patch -p1 -f < %(allsrcdir)s/%(patch)s || true
''',
                     locals ())

    def pre_install_smurf_exe (self):
        for i in self.locate_files ('%(builddir)s', '*.exe'):
            base = os.path.splitext (i)[0]
            self.system ('''mv %(i)s %(base)s''', locals ())

    def post_install_smurf_exe (self):
        import os
        for i in (self.locate_files ('%(install_root)s/bin', '*')
                  + self.locate_files ('%(install_root)s/usr/bin', '*')):
            if (not os.path.islink (i)
                and not os.path.splitext (i)[1]
                and self.read_pipe ('file -b %(i)s', locals ()).startswith ('MS-DOS executable PE')):
                self.system ('''mv %(i)s %(i)s.exe''', locals ())

    def install_readmes (self):
        self.system ('''
mkdir -p %(install_root)s/usr/share/doc/%(name)s
''')
        import glob
        for i in glob.glob ('%(srcdir)s/[A-Z]*'
                            % self.get_substitution_dict ()):
            import shutil
            if (os.path.isfile (i)
                and not os.path.basename (i).startswith ('Makefile')
                and not os.path.basename (i).startswith ('GNUmakefile')):
                shutil.copy2 (i, '%(install_root)s/usr/share/doc/%(name)s'
                              % self.get_substitution_dict ())

    def build_version (self):
        "the version in the shipped package."
        # FIXME: ugly workaround needed for lilypond package...
        return '%(version)s'

    def build_number (self):
        # FIXME: actually need the packages' build number here...
        build_number_file = '%(topdir)s/buildnumber-%(lilypond_branch)s.make'
        d = misc.grok_sh_variables (self.expand (build_number_file))
        b = '%(INSTALLER_BUILD)s' % d
        return b

    def with_vc (self, repo):
        self.vc_repository = repo
        
    def with (self,
              mirror=download.gnu,
              version='',
              module='',
              branch='',
              revision='',
              format='gz'):

        self.format = format
        self.ball_version = version
        self.revision = revision
        self.url = mirror

        if self.vc_repository:
            self.vc_commit = self.ball_version
        else:
            self.vc_commit = misc.split_version (self.ball_version)[0]
        
        self.ball_version = version

        ## don't do substitution. We want to postpone
        ## generating the dict until we're sure it doesn't change.

        return self

    def lib_rewire (self):
        # Rewire absolute names and symlinks.
        # Better to create relative ones?
        for i in glob.glob (self.expand ('%(srcdir)s/root/usr/lib/lib*.so')):
            if os.path.islink (i):
                s = os.readlink (i)
                if s.startswith ('/'):
                    os.remove (i)
                    os.symlink (self.settings.system_root + s, i)

class BinarySpec (BuildSpec):
    def untar (self):
        self.system ('''
rm -rf %(srcdir)s %(builddir)s %(install_root)s
''')
        self.system ('mkdir -p %(srcdir)s/root')
        self._untar ('%(srcdir)s/root')

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

        _verbose = ''
        if self.verbose:
            _verbose = ' -v'
        self.system ('tar -C %(srcdir)s/root -cf- . | tar -C %(install_root)s%(_verbose)s -xf-', env=locals ())
        self.libtool_installed_la_fixups ()

    def get_subpackage_names (self):
        # FIXME: splitting makes that cygwin's gettext + -devel subpackage
        # gets overwritten by cygwin's gettext-devel + '' base package
        return ['']

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
        return self.srcdir()

class Change_target_dict:
    def __init__ (self, package, override):
        self._target_dict_method = package.get_substitution_dict
        self._add_dict = override

    def target_dict (self, env={}):
        env_copy = env.copy()
        env_copy.update (self._add_dict)
        d = self._target_dict_method (env_copy)
        return d

    def append_dict (self, env= {}):

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

def get_base_package_name (name):
    name = re.sub ('-devel$', '', name)

    # breaks mingw dep resolution, mingw-runtime
    ##name = re.sub ('-runtime$', '', name)
    name = re.sub ('-doc$', '', name)
    return name
