import inspect
import os
import re
import sys
#
from gub.syntax import printf
from gub import commands
from gub import context
from gub import guppackage
from gub import loggedos
from gub import logging
from gub import misc
from gub import octal

class Build (context.RunnableContext):
    '''How to build a piece of software

    TODO: move all non configure-make-make install stuff from
    AutoBuild here
    '''

    source = ''
    branch = ''

    def __init__ (self, settings, source):
        context.RunnableContext.__init__ (self, settings)
        self.source = source
        self.settings = settings
        self.source.connect_logger (logging.default_logger)

    def connect_command_runner (self, runner):
        if runner:
            self.source.connect_logger (runner.logger)
        return context.RunnableContext.connect_command_runner (self, runner)

    @context.subst_method
    def checksum_file (self):
        return '%(packages)s/%(name)s%(vc_branch_suffix)s.checksum'

    def nop (self):
        pass
    def stages (self):
        return list ()
    def apply_patch (self, patch, strip_components=1):
        name, parameters = misc.dissect_url (patch)
        strip = str (strip_components)
        strip = parameters.get ('strip', [strip])[0]
        strip = parameters.get ('strip_components', [strip])[0]
        self.system ('''
cd %(srcdir)s && patch -p%(strip)s < %(patchdir)s/%(name)s
''', locals ())
    def build (self):
        available = dict (inspect.getmembers (self,
                                              lambda x: hasattr (x, '__call__')))
        stages = self.stages ()
        tainted = False
        for stage in stages:
            if (stage not in available):
                continue

            if self.is_done (stage, stages.index (stage)):
                tainted = True
                continue

            self.runner.stage (' *** Stage: %s (%s, %s)\n'
                               % (stage, self.name (),
                                  self.settings.platform))

            if (stage == 'package' and tainted):
                msg = self.expand ('''This compile has previously been interrupted.
To ensure a repeatable build, this will not be packaged.

Use

rm %(stamp_file)s

to force rebuild, or

--force-package

to skip this check.
''')
                logging.error (msg)
                #FIXME: throw exception.  this plays nice with
                # buildrunner and with bin/gub, so check that.
                sys.exit (1)
            try:
                (available[stage]) ()
            except:
                t, v, b = sys.exc_info ()
                if t == misc.SystemFailed:
                    # A failed patch will leave system in unpredictable state.
                    if stage == 'patch':
                        self.system ('rm %(stamp_file)s')
                raise

            if stage != 'clean':
                self.set_done (stage, stages.index (stage))

class AutoBuild (Build):
    '''Build a source package the traditional Unix way

    Based on the traditional configure; make; make install, this class
    tries to do everything including autotooling and libtool fooling.  '''

    def __init__ (self, settings, source):
        Build.__init__ (self, settings, source)
        self._dependencies = None
        self._build_dependencies = None
        self.split_packages = []
        self.so_version = '1'

    def stages (self):
        lst = ['untar', 'patch', 'autoupdate',
               'configure', 'compile', 'install',
               'src_package', 'package', 'clean']
        # see bin/gub TODO 'src_package',
        if self.settings.platform != 'cygwin':
            lst = [s for s in lst if s != 'src_package']
        return lst

    def configure_prepares_builddir (self):
        return True

    @context.subst_method
    def LD_PRELOAD (self):
        return '%(tools_prefix)s/lib/librestrict.so'

    @context.subst_method
    def rpath (self):
#        return r'-Wl,-rpath -Wl,\$$ORIGIN/../lib -Wl,-rpath -Wl,\$$ORIGIN/../../lib'
        return r'-Wl,-rpath -Wl,\$$ORIGIN/../lib'

    def get_substitution_dict (self, env={}):
        dict = {
            'CPATH': '',
            'CPLUS_INCLUDE_PATH': '',
            'C_INCLUDE_PATH': '',
            'LIBRARY_PATH': '/empty-means-cwd-in-feisty',
            }
        dict.update (env)
        d = context.RunnableContext.get_substitution_dict (self, dict).copy ()
        return d

    def class_invoke_version (self, klas, name):
        name_version = name + '_' + self.version ().replace ('.', '_')
        if name_version in klas.__dict__:
            klas.__dict__[name_version] (self)

    def download (self):
        self.source.download ()

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

    @context.subst_method
    def name (self):
        file = self.__class__.__module__
        file = re.sub ('_xx_', '++', file)
        file = re.sub ('_x_', '+', file)
        return file

    @context.subst_method
    def pretty_name (self):
        name = self.__class__.__name__
        name = re.sub ('__.*', '', name)
        return name

    @context.subst_method
    def file_name (self):
        return self.source.file_name ()

    @context.subst_method
    def source_checksum (self):
        return self.source.checksum ()

    def license_files (self):
        return ['%(srcdir)s/COPYING',
                '%(srcdir)s/COPYING.LIB',
                '%(srcdir)s/LICENSE',
                '%(srcdir)s/LICENCE',]

    @context.subst_method
    def basename (self):
        return misc.ball_basename (self.file_name ())

    @context.subst_method
    def packaging_suffix_dir (self):
        return ''

    @context.subst_method
    def full_version (self):
        return self.version ()

    @context.subst_method
    def build_dependencies_string (self):
        deps = sorted (set (self.get_build_dependencies ()))
        return ';'.join (deps)

    # FIXME: move version/branch/tracking macramee to Repository
    @context.subst_method
    def ball_suffix (self):
        # FIXME: ball suffix is also used by %(srcdir)s
        # for tracking repositories, the name of the source and
        # build dir must stay the same.
        if self.source.is_tracking ():
            return self.vc_branch_suffix ()
        return '-' + self.source.version ()

    @context.subst_method
    def vc_branch (self):
        return self.source.full_branch_name ()

    @context.subst_method
    def vc_branch_suffix (self):
        b = self.vc_branch ()
        if b:
            b = '-' + b
        return b

    @context.subst_method
    def version (self):
        return self.source.version ()

    @context.subst_method
    def name_version (self):
        return '%s-%s' % (self.name (), self.version ())

    @context.subst_method
    def srcdir (self):
        return '%(allsrcdir)s/%(name)s%(ball_suffix)s'

    @context.subst_method
    def builddir (self):
        return '%(allbuilddir)s/%(name)s%(ball_suffix)s'

    @context.subst_method
    def install_root (self):
        return '%(installdir)s/%(name)s-%(version)s-root'

    @context.subst_method
    def install_prefix (self):
        return '%(install_root)s%(prefix_dir)s'

    @context.subst_method
    def install_command (self):
        return '''make %(makeflags)s DESTDIR=%(install_root)s install'''

    @context.subst_method
    def autodir (self):
        return '%(srcdir)s'

    def aclocal_path (self):
        return ['%(system_prefix)s/share/aclocal']

    @context.subst_method
    def configure_binary (self):
        return '%(autodir)s/configure'

    @context.subst_method
    def configure_command (self):
        return '%(configure_binary)s --prefix=%(install_prefix)s'

    @context.subst_method
    def compile_command (self):
        return 'make %(makeflags)s '

    # what the heck is this?  Why would we not want to use
    # -j x with multiple cpu's (compiling is often io bound)
    # and why not when cross compiling (think icecc?).
    @context.subst_method
    def native_compile_command (self):
        c = 'make'

        job_spec = ' '
        if (not self.force_sequential_build ()
            and self.settings.cpu_count_str != '1'):

            job_spec += ' -j%s ' % self.settings.cpu_count_str

        c += job_spec
        return c

    @context.subst_method
    def src_package_ball (self):
        return '%(src_package_uploads)s/%(name)s%(ball_suffix)s-src.%(platform)s.tar.gz'

    @context.subst_method
    def src_package_uploads (self):
        return '%(packages)s'

    @context.subst_method
    def stamp_file (self):
        return '%(statusdir)s/%(name)s-%(version)s-%(source_checksum)s'

    @context.subst_method
    def makeflags (self):
        return ''

    @context.subst_method
    def cache_file (self):
        return '%(builddir)s/config.cache'

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

    def patch (self):
        list (map (self.apply_patch, self.__class__.__dict__.get ('patches', [])))

    def force_autoupdate (self):
        return False

    def autoupdate (self):
        # FIMXE: can we do this smarter?
        if self.force_autoupdate ():
            self.runner._execute (commands.ForcedAutogenMagic (self))
        else:
            self.runner._execute (commands.AutogenMagic (self))

    def config_cache_overrides (self, str):
        return str

    def config_cache_settings (self):
        return self.config_cache_overrides ('')

    def config_cache (self):
        str = self.config_cache_settings ()
        if str:
            self.system ('mkdir -p %(builddir)s || true')
            self.dump (str, self.cache_file (), permissions=octal.o755)

    def configure (self):
        self.config_cache ()
        self.system ('''
mkdir -p %(builddir)s || true
cd %(builddir)s && chmod +x %(configure_binary)s && %(configure_command)s
''')
        self.map_locate (libtool_disable_install_not_into_dot_libs_test, '%(builddir)s', 'libtool')

    def shadow (self):
        self.system ('rm -rf %(builddir)s')
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')

    def compile (self):
        self.system ('cd %(builddir)s && %(compile_command)s')

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

    def update_config_guess_config_sub (self):
        guess = self.expand ('%(system_prefix)s/share/libtool/config.guess')
        sub = self.expand ('%(system_prefix)s/share/libtool/config.sub')
        for file in guess, sub:
            self.system ('cp -pv %(file)s %(autodir)s',  locals ())

    def update_libtool (self):
        self.map_locate (lambda logger, file: libtool_update (logger, self.expand ('%(system_prefix)s/bin/libtool'), file), '%(builddir)s', 'libtool')

    def install (self):
        '''Install package into %(install_root).

        Any overrides should follow this command, since it will erase the old
        install_root first.

        FIXME: this is partly totally broken, some overrides need to
        be done BEFORE the rest of the install stage.  We need to
        figure out some clean way to plug something in between the
        automatic cleaning, and the rest of the install.'''

        self.system ('''
rm -rf %(install_root)s
cd %(builddir)s && %(install_command)s
rm -f \
    %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/info/dir \
    %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/info/dir.old \
    %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/share/info/dir \
    %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s/share/info/dir.old \
    %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s%(cross_dir)s/info/dir \
    %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s%(cross_dir)s/info/dir.old \
    %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s%(cross_dir)s/share/info/dir \
    %(install_root)s%(packaging_suffix_dir)s%(prefix_dir)s%(cross_dir)s/share/info/dir.old \
''')
        self.install_license ()
        self.libtool_installed_la_fixups ()

    def install_license (self):
        def install (logger, lst):
            for file in lst:
                if os.path.exists (file):
                    cmd = self.expand ('''
mkdir -p %(install_root)s/license
cp %(file)s %(install_root)s/license/%(name)s
''', locals ())
                    loggedos.system (logger, cmd)
                    return
        self.func (install, list (map (self.expand, self.license_files ())))

    def libtool_installed_la_fixups (self):
        def installed_la_fixup (logger, la):
            (dir, base) = os.path.split (la)
            base = base[3:-3]
            dir = re.sub (r"^\./", "/", dir)

            loggedos.file_sub (logger, [(''' *-L *[^\"\' ][^\"\' ]*''', ''),
                    (self.expand ('''( |=|\')(/[^ ]*usr/lib|%(targetdir)s.*)/lib([^ \'/]*)\.(a|la|so)[^ \']*'''),
                    '\\1-l\\3 '),
                    ('^old_library=.*',
                     self.expand ("""old_library='lib%(base)s.a'""", env=locals ())),
                    ],
                   la)
            if self.settings.platform.startswith ('mingw'):

                loggedos.file_sub (logger, [('library_names=.*',
                                 self.expand ("library_names='lib%(base)s.dll.a'", env=locals ()))],
                               la)

        self.map_locate (installed_la_fixup, '%(install_root)s', 'lib*.la')

    def rewire_symlinks (self):
        def rewire (logger, file):
            if os.path.islink (file):
                s = os.readlink (file)
                if s.startswith ('/') and self.settings.system_root not in s:
                    new_dest = os.path.join (self.settings.system_root, s[1:])
                    loggedos.remove (logger, file)
                    loggedos.symlink (logger, new_dest, file)

        self.map_locate (rewire, '%(install_root)s', '*',
                         silent=True)

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

    def with_platform (self, name):
        return misc.with_platform (name, self.settings.platform)

    def get_platform_build_dependencies (self):
        return [self.with_platform (n) for n in self.get_build_dependencies ()]

    def platform_name (self):
        return self.with_platform (self.name ())

    def platform (self):
        return self.settings.platform

    def get_subpackage_definitions (self):
        cross_dir = self.settings.cross_dir
        prefix_dir = self.settings.prefix_dir
        d = {
            'base': [prefix_dir + '/share'],
            'common': [prefix_dir + '/share'],
            'devel': [
            prefix_dir + '/bin/*-config',
            prefix_dir + '/include',
            prefix_dir + cross_dir + '/bin',
            prefix_dir + cross_dir + '/include',
            prefix_dir + cross_dir + '/lib',
            prefix_dir + cross_dir + '/libexec',
            prefix_dir + cross_dir + '/' + self.settings.target_architecture,
            prefix_dir + '/share/aclocal',
            prefix_dir + '/lib/lib*.a',
            prefix_dir + '/lib/pkgconfig',
            ],
            'doc': [
            prefix_dir + '/share/doc',
            prefix_dir + '/share/gtk-doc',
            prefix_dir + '/share/info',
            prefix_dir + '/share/man',
            prefix_dir + cross_dir + '/info',
            prefix_dir + cross_dir + '/man',
            ],
            'runtime': ['/lib', prefix_dir + '/lib', prefix_dir + '/share'],
            'x11': [prefix_dir + '/X11', prefix_dir + '/X11R6'],
            '' : ['/'],
            }
        return d

    def get_subpackage_names (self):
        return ['devel', 'doc', '']

    # FIXME: when only patched in via MethodOverride, the real descr_dict,
    # category_dict are not pickled and cygwin packaging fails
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

            p = guppackage.GupPackage (self.runner)
            # FIXME: feature envy -> GupPackage constructor/factory
            p._file_specs = filespecs

            p.set_dict (self.get_substitution_dict (), sub)

            conflict_str = ';'.join (conflict_dict.get (sub, []))
            if 'conflicts_string' in p._dict:
                conflict_str = p._dict['conflicts_string'] + ';' + conflict_str
            p._dict['conflicts_string'] = conflict_str

            dep_str = ';'.join (map (self.with_platform, dep_dict.get (sub, [])))
            dep_str = ';'.join (dep_dict.get (sub, []))
            if 'dependencies_string' in p._dict:
                dep_str = p._dict['dependencies_string'] + ';' + dep_str
            p._dict['dependencies_string'] = dep_str

            # FIXME make generic: use cross.get_subpackage_dict_methods () or similar.
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
        _v = '' #self.os_interface.verbose_flag ()
        self.system ('''
tar -C %(allsrcdir)s --exclude "*~" --exclude "*.orig"%(_v)s -zcf %(src_package_ball)s %(dir_name)s
''',
                     locals ())

    def clean (self):
        self.system ('rm -rf  %(stamp_file)s %(install_root)s', locals ())
        if self.source.is_tracking ():
            # URG
            return
        self.system ('''rm -rf %(srcdir)s %(builddir)s''', locals ())

    def untar (self):
        self.runner._execute (commands.UpdateSourceDir (self))

    def pre_install_smurf_exe (self):
        def un_exe (logger, file):
            base = os.path.splitext (file)[0]
            loggedos.system (logger, self.expand ('mv %(file)s %(base)s', locals ()))
        self.map_locate (un_exe, '%(builddir)s', '*.exe')

    def post_install_smurf_exe (self):
        def add_exe (logger_why_already_in_self, file):
            if (not os.path.islink (file)
                and not os.path.splitext (file)[1]
                and loggedos.read_pipe (logger_why_already_in_self, self.expand ('file -b %(file)s', locals ())).startswith ('MS-DOS executable PE')):
                loggedos.system (logger_why_already_in_self, self.expand ('mv %(file)s %(file)s.exe', locals ()))
        self.map_locate (add_exe, '%(install_root)s/bin', '*')
        self.map_locate (add_exe, '%(install_prefix)s/bin', '*')

    def install_readmes (self):
        cmd = self.system ('''
mkdir -p %(install_prefix)s/share/doc/%(name)s
''')
        def copy_readme (logger, file):
            if (os.path.isfile (file)
                and not os.path.basename (file).startswith ('Makefile')
                and not os.path.basename (file).startswith ('GNUmakefile')):
                loggedos.system (logger, self.expand ('cp %(file)s %(install_prefix)s/share/doc/%(name)s', locals ()))
        self.map_locate (copy_readme, '%(srcdir)s', '[A-Z]*')

    def build_version (self):
        "the version in the shipped package."
        # FIXME: ugly workaround needed for lilypond package...
        return '%(version)s'

    # Used in mingw python and liblpsolve.  Better replace this by
    # fixing the gcc linking command?
    def generate_dll_a_and_la (self, libname, depend=''):
        # ugh, atexit, _onexit mutliply defined in crt2.o
        self.system (misc.join_lines ('''
cd %(install_prefix)s
&& echo EXPORTS > lib/lib%(libname)s.a.def
&& %(toolchain_prefix)snm bin/lib%(libname)s.dll | grep ' T _' | sed -e 's/.* T _//' | grep -Ev '^(atexit|_onexit)$' >> lib/lib%(libname)s.a.def
&& (grep '@' lib/lib%(libname)s.a.def | sed -e 's/@.*//' >> lib/lib%(libname)s.a.def || :)
&& %(toolchain_prefix)sdlltool --def lib/lib%(libname)s.a.def --dllname bin/lib%(libname)s.dll --output-lib lib/lib%(libname)s.dll.a
'''), locals ())
        self.file_sub ([('LIBRARY', '%(libname)s'),
                        ('STATICLIB', ''),
                        ('DEPEND', ' %(depend)s'),
                        ('LIBDIR', '%(prefix_dir)s/lib')],
                       '%(sourcefiledir)s/libtool.la',
                       '%(install_prefix)s/lib/lib%(libname)s.la', env=locals ())

class BinaryBuild (AutoBuild):
    def stages (self):
        return ['untar', 'install', 'package', 'clean']
    def install (self):
        self.system ('mkdir -p %(install_root)s')
        _v = '' #self.os_interface.verbose_flag ()
        self.system ('tar -C %(srcdir)s -cf- . | tar -C %(install_root)s%(_v)s -p -xf-', env=locals ())
        self.libtool_installed_la_fixups ()
    def get_subpackage_names (self):
        # FIXME: splitting makes that cygwin's gettext + -devel subpackage
        # gets overwritten by cygwin's gettext-devel + '' base package
        return ['']

class NullBuild (AutoBuild):
    """Placeholder for downloads """
    def stages (self):
        return ['patch', 'install', 'package', 'clean']
    def get_subpackage_names (self):
        return ['']
    def install (self):
        self.system ('mkdir -p %(install_root)s')

class SdkBuild (NullBuild):
    def stages (self):
        return ['untar', 'patch', 'install', 'package', 'clean']
    def install_root (self):
        return self.srcdir ()

def libtool_disable_install_not_into_dot_libs_test (logger, file):
    '''libtool: install: error: cannot install `libexslt.la' to a directory not ending in /home/janneke/vc/gub/target/mingw/build/libxslt-1.1.24/libexslt/.libs'''
    loggedos.file_sub (logger, [(r'if test "\$inst_prefix_dir" = "\$destdir"; then',
                                 'if false && test "$inst_prefix_dir" = "$destdir"; then')],
                       file)

def libtool_update (logger, libtool, file):
    if not os.path.exists (libtool):
        message = 'Cannot update libtool: no such file: %(libtool)s' % locals ()
        logger.write_log (message, 'error')
        raise Exception (message)
    loggedos.system (logger, 'cp %(file)s %(file)s~' % locals ())
    loggedos.system (logger, 'cp %(libtool)s %(file)s' % locals ())
    libtool_disable_install_not_into_dot_libs_test (logger, file)
    loggedos.system (logger, 'chmod 755  %(file)s' % locals ())

def libtool_force_infer_tag (logger, tag, file):
    ''' libtool: compile: unable to infer tagged configuration '''
    loggedos.file_sub (logger, [('^func_infer_tag ', '''func_infer_tag ()
{
    tagname=%(tag)s
}

old_func_infer_tag ''' % locals ())], file)

def libtool_force_infer_tag_CXX (logger, file):
    ''' CXX seems the only valid tag name? '''
    libtool_force_infer_tag (logger, 'CXX', file)

def libtool_update_preserve_CC (logger, libtool, file):
    CC_re = '^CC="([^"]*)"'
    orig_CC = re.search ('(?m)' + CC_re, open (file).read ()).group (0)
    libtool_update (logger, libtool, file)
    loggedos.file_sub (logger, [(CC_re, orig_CC)], file)

def libtool_update_preserve_vars (logger, libtool, vars, file):
    printf ('preserve: ', file)
    old = open (file).read ()
    open (file + '.old', 'w').write (old)
    libtool_update (logger, libtool, file)
    new = open (file).read ()
    open (file + '.new', 'w').write (new)
    def subst_vars (o, n):
        for v in vars:
            v_re = '(?m)^%(v)s="([^"]*)"' % locals ()
            orig_m = re.search (v_re, o)
            if not orig_m:
                # some generated libtool thingies only have the first part
                # but vars in the second part must always be substituted
                printf ('from first part')
                orig_m = re.search (v_re, old)
            if orig_m:
                b = n
                n = re.sub (v_re, orig_m.group (0), n)
                printf ('replace:', orig_m.group (0))
                if b == n:
                    printf ('NODIFF:', v_re)
            else:
                printf ('not found:', v_re)
        return n
    # libtool comes in two parts which define the same/similar variables
    marker = '\nexit '
    n1 = subst_vars (old[:old.find (marker)], new[:new.find (marker)])
    n2 = subst_vars (old[old.find (marker):], new[new.find (marker):])
    open (file, 'w').write (n1 + n2)
    loggedos.chmod (logger, file, octal.o755)
