import os
#
from gub import context
from gub import loggedos
from gub import misc
from gub import repository
from gub import target
from gub import versiondb

class LilyPond (target.AutoBuild):
    source = 'git://git.sv.gnu.org/lilypond.git'
    branch = 'master'

    '''A program for printing sheet music
    LilyPond lets you create music notation.  It produces
    beautiful sheet music from a high-level description file.'''

    @staticmethod
    def version_from_VERSION (self):
        try:
            s = self.read_file ('VERSION')
            if 'MAJOR_VERSION' in s:
                d = misc.grok_sh_variables_str (s)
                return '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
        except:
            pass
        return '0.0.0'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        # FIXME: should add to C_INCLUDE_PATH
        builddir = self.builddir ()
        self.target_gcc_flags = (settings.target_gcc_flags
                                 + ' -I%(builddir)s' % locals ())
        if isinstance (source, repository.Git):
            source.version = misc.bind_method (LilyPond.version_from_VERSION, source)
    def get_subpackage_names (self):
        return ['']
    def _get_build_dependencies (self):
        return ['fontconfig-devel',
                'freetype-devel',
                'gettext-devel',
                'ghostscript',
                'guile-devel',
                'pango-devel',
                'python-devel',
                'urw-fonts',
                'tools::autoconf',
                'tools::flex',
                'tools::bison',
                'tools::texinfo', # nonstandard
                'tools::fontforge',
                'tools::pkg-config', # nonstandard (MacOS)
                'tools::gettext', # AM_GNU_GETTEXT
                'tools::t1utils',
                'tools::texi2html',
                #'tools::mpost ', 
                ]
    def autoupdate (self):
        self.system ('cd %(srcdir)s && ./smart-autogen.sh --noconfigure') 
    def configure_binary (self):
        return '%(srcdir)s/smart-configure.sh'
    def configure (self):
        self.system ('mkdir -p %(builddir)s || true')
        self.system ('cp %(tools_prefix)s/include/FlexLexer.h %(builddir)s/')
        target.AutoBuild.configure (self)
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + misc.join_lines ('''
--enable-relocation
--enable-rpath
--disable-documentation
--with-ncsb-dir=%(system_prefix)s/share/fonts/default/Type1
'''))
    def name_version (self):
        return target.AutoBuild.name_version (self)
    def build_version (self):
        v = self.source.version ()
        self.runner.info ('LILYPOND-VERSION: %(v)s\n' % locals ())
        return v
    def pretty_name (self):
        return 'LilyPond'
    def makeflags (self):
        return ' TARGET_PYTHON=/usr/bin/python'
    def install (self):
        target.AutoBuild.install (self)
        # FIXME: This should not be in generic package, for installers only.
        self.installer_install_stuff ()
    def installer_install_stuff (self):
        # FIXME: is it really the installer version that we need here,
        # or do we need the version of lilypond?
        installer_version = self.build_version ()
        # WTF, current.
        self.system ('cd %(install_prefix)s/share/lilypond && mv %(installer_version)s current',
                     locals ())

        self.system ('cd %(install_prefix)s/lib/lilypond && mv %(installer_version)s current',
                     locals ())

        self.system ('mkdir -p %(install_prefix)s/etc/fonts/')
        self.dump ('''
<fontconfig>
<selectfont>
 <rejectfont>
 <pattern>
  <patelt name="scalable"><bool>false</bool></patelt>
 </pattern>
 </rejectfont>
</selectfont>

<cachedir>~/.lilypond-fonts.cache-2</cachedir>
</fontconfig>
''', '%(install_prefix)s/etc/fonts/local.conf', 'w', locals ())
    def gub_name (self):
        nv = self.name_version ()
        p = self.settings.platform
        return '%(nv)s.%(p)s.gub' % locals ()

class LilyPond__cygwin (LilyPond):

    def get_subpackage_names (self):
        return ['doc', '']

    def get_dependency_dict (self): #cygwin
        return {
            '' :
            [
            'glib2',
            'guile-runtime',
            'fontconfig-runtime', ## CYGWIN name: 'libfontconfig1',
            #'freetype2-runtime', ## CYGWIN name: 'libfreetype26',
            'libfreetype26',
            'libiconv2',
            'libintl8', 'libintl3',
            'pango-runtime',
            'python',
            ]
            + [
            'bash',
            'coreutils',
            'cygwin',
            'findutils',
            'ghostscript',
            ],
            'doc': ['texinfo'],
            }

    def get_build_dependencies (self): #cygwin

        #FIXME: aargh, MUST specify bash, coreutils etc here too.
        # If get_dependency_dict () lists any packages not
        # part of build_dependencies, we get:

        # Using version number 2.8.6 unknown package bash
        # installing package: bash
        # Traceback (most recent call last):
        #   File "installer-builder.py", line 171, in ?
        #     main ()
        #   File "installer-builder.py", line 163, in main
        #     run_installer_commands (cs, settings, commands)
        #   File "installer-builder.py", line 130, in run_installer_commands
        #     build_installer (installer_obj, args)
        #   File "installer-builder.py", line 110, in build_installer
        #     install_manager.install_package (a)
        #   File "lib/gup.py", line 236, in install_package
        #     d = self._packages[name]
        # KeyError: 'bash'

        return [
            'gettext-devel',
            ## FIXME: for distro we don't use get_base_package_name,
            ## so we cannot use split-package names for gub/source
            ## build dependencies
            ##'guile-devel',
            'guile',
            'python',
            ##'fontconfig', ## CYGWIN: 'libfontconfig-devel',
            'libfontconfig-devel',
            ##'freetype2', ## CYGWIN: 'libfreetype2-devel',
            'libfreetype2-devel',
            # cygwin bug: pango-devel should depend on glib2-devel
            'pango-devel', 'glib2-devel',
            'urw-fonts'] + [
            'bash',
            'coreutils',
            'findutils',
            'ghostscript',
            'lilypond-doc',
            ]
    def configure_command (self):
        return (LilyPond.configure_command (self)
                .replace ('--enable-relocation', '--disable-relocation'))
    def makeflags (self):
        python_lib = '%(system_prefix)s/bin/libpython*.dll'
        LDFLAGS = '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api'
        return (LilyPond.makeflags (self)
                + ' LDFLAGS="%(LDFLAGS)s %(python_lib)s"' % locals ())
    def compile (self):
        # Because of relocation script, python must be built before scripts
        self.system ('''
cd %(builddir)s && make -C python %(makeflags)s
cd %(builddir)s && make -C scripts %(makeflags)s
cp -pv %(system_prefix)s/share/gettext/gettext.h %(system_prefix)s/include''')
        LilyPond.compile (self)
    def install (self):
        ##LilyPond.install (self)
        target.AutoBuild.install (self)
        self.install_doc ()
    def install_doc (self):
        # lilypond.make uses `python gub/versiondb.py --build-for=2.11.32'
        # which only looks at source ball build numbers, which are always `1'
        # This could be fixed, but for now just build one doc ball per release?
        installer_build = '1'
        installer_version = self.build_version ()
        docball = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.documentation.tar.bz2', env=locals ())

        self.system ('''
mkdir -p %(install_prefix)s/share/doc/lilypond
tar -C %(install_prefix)s -jxf %(docball)s
''',
                  locals ())

    def category_dict (self):
        return {'': 'Publishing'}

## shortcut: take python out of dependencies
class LilyPond__no_python (LilyPond):
    def _get_build_dependencies (self):
        return [x for x in LilyPond._get_build_dependencies (self)
                if x != 'python-devel']
    def configure (self):
        self.system ('mkdir -p %(builddir)s || true') 
        self.system ('touch %(builddir)s/Python.h') 
        LilyPond.configure (self)
        self.dump ('''
all:
        true

install:
        -mkdir -p $(DESTDIR)%(prefix_dir)s/lib/lilypond/%(version)s
''', '%(builddir)s/python/GNUmakefile')
        
class LilyPond__mingw (LilyPond):
    def _get_build_dependencies (self):
        return (LilyPond._get_build_dependencies (self)
                + ['lilypad', 'tools::icoutils', 'tools::nsis'])
    def makeflags (self):
        python_lib = '%(system_prefix)s/bin/libpython*.dll'
        return (LilyPond.makeflags (self)
                + ' LDFLAGS="%(python_lib)s"'  % locals ())
    # ugh Python hack: C&P Cygwin
    def compile (self):
        # Because of relocation script, python must be built before scripts
        self.system ('''
cd %(builddir)s/lily && rm -f out/lilypond || :
cd %(builddir)s && make -C python %(makeflags)s
cd %(builddir)s && make -C scripts %(makeflags)s
#cp -pv %(system_prefix)s/share/gettext/gettext.h %(system_prefix)s/include
''')
        LilyPond.compile (self)
        self.system ('''
cd %(builddir)s/lily && mv out/lilypond out/lilypond-console
cd %(builddir)s/lily && make MODULE_LDFLAGS="-mwindows" && mv out/lilypond out/lilypond-windows
cd %(builddir)s/lily && touch out/lilypond
''')
    def configure (self):
        LilyPond.configure (self)
        ## huh, why ? --hwn
        ## self.config_cache ()
        ## for console: no -mwindows
        self.file_sub ([(' -mwindows', ' '),
                ## gdb doesn't work on windows anyway.
                (' -g ', ' '),
                ],
               '%(builddir)s/config.make')
    def install (self):
        LilyPond.install (self)
        self.system ('''
rm -f %(install_prefix)s/bin/lilypond-windows
install -m755 %(builddir)s/lily/out/lilypond-windows %(install_prefix)s/bin/lilypond-windows.exe
rm -f %(install_prefix)s/bin/lilypond
install -m755 %(builddir)s/lily/out/lilypond-console %(install_prefix)s/bin/lilypond.exe
cp %(install_prefix)s/lib/lilypond/*/python/* %(install_prefix)s/bin
cp %(install_prefix)s/share/lilypond/*/python/* %(install_prefix)s/bin
''')
        def rename (logger, name):
            header = open (name).readline ().strip ()
            if header.endswith ('guile'):
                loggedos.system (logger, 'mv %(name)s %(name)s.scm' % locals ())
            elif header.endswith ('python') and not name.endswith ('.py'):
                loggedos.system (logger, 'mv %(name)s %(name)s.py' % locals ())
        def asciify (logger, name):
            loggedos.file_sub (logger, [('\r*\n', '\r\n')], name)
        self.map_locate (rename, self.expand ('%(install_prefix)s/bin/'), '*')
        self.map_locate (asciify, self.expand ('%(install_root)s'), '*.ly')
        bat = r'''@echo off
"@INSTDIR@\usr\bin\lilypond-windows.exe" -dgui %1 %2 %3 %4 %5 %6 %7 %8 %9
'''.replace ('%', '%%').replace ('\n', '\r\n')
            
        self.dump (bat, '%(install_prefix)s/bin/lilypond-windows.bat.in')

## please document exactly why if this is switched back.
#        self.file_sub ([(r'gs-font-load\s+#f', 'gs-font-load #t')],
#        '%(install_prefix)s/share/lilypond/current/scm/lily.scm')

class LilyPond__debian (LilyPond):
    def get_dependency_dict (self): #debian
        from gub import debian, gup
        return {'': gup.gub_to_distro_deps (LilyPond.get_dependency_dict (self)[''],
                                            debian.gub_to_distro_dict)}
    def compile (self):
        # Because of relocation script, python must be built before scripts
        self.system ('''
cd %(builddir)s && make -C python %(makeflags)s
cd %(builddir)s && make -C scripts %(makeflags)s
''')
        LilyPond.compile (self)
    def install (self):
        target.AutoBuild.install (self)
    def get_build_dependencies (self): # debian
        #FIXME: aargh, MUST specify gs,  etc here too.
        return [
            'gettext',
            'guile-1.8-dev',
            'libfontconfig1-dev',
            'libfreetype6-dev',
            'libglib2.0-dev',
            'python2.4-dev',
            'libpango1.0-dev',
            'zlib1g-dev',
            'urw-fonts',
            ] + ['gs']

class LilyPond__darwin (LilyPond):
    def _get_build_dependencies (self):
        return (LilyPond._get_build_dependencies (self)
                + [ 'fondu', 'osx-lilypad'])
    def configure_command (self):
        return (LilyPond.configure_command (self)
                .replace ('--enable-rpath', '--disable-rpath'))

class LilyPond__darwin__ppc (LilyPond__darwin):
    def configure (self):
        LilyPond__darwin.configure (self)
        self.dump ('CXXFLAGS += -DGUILE_ELLIPSIS=...',
                   '%(builddir)s/local.make')

class LilyPond_base (target.AutoBuild):
    source = LilyPond.source
    never_install = 'True'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        source.dir = os.path.join (self.settings.downloads, 'lilypond')
        source.version = misc.bind_method (LilyPond.version_from_VERSION, source)
        source.is_tracking = misc.bind_method (lambda x: True, source)
        source.is_downloaded = misc.bind_method (lambda x: True, source)
        source.update_workdir = misc.bind_method (lambda x: True, source)
    def _get_build_dependencies (self):
        return [self.settings.build_platform + '::lilypond']
    def get_subpackage_names (self):
        return ['']
    def stages (self):
        return ['compile', 'install', 'package']
    def builddir (self):
        #URWGSGSEWNG
        return '%(allbuilddir)s/lilypond%(ball_suffix)s'
    def srcdir (self):
        #URWGSGSEWNG
        return '%(allsrcdir)s/lilypond%(ball_suffix)s'
    @context.subst_method
    def build_number (self):
        vdb = versiondb.VersionDataBase (os.path.join (self.settings.uploads,
                                                       'lilypond.versions'))
        vdb.get_binaries_from_url ('http://lilypond.org/download/')
        vdb.write ()
        return str (vdb.get_next_build_number (misc.string_to_version (self.version ())))
    @context.subst_method
    def doc_limits (self):
        if '64' in self.settings.build_platform:
            return 'ulimit -m 512000 && ulimit -d 512000 && ulimit -v 1024000 '
        return 'ulimit -m 256000 && ulimit -d 256000 && ulimit -v 384000 '
    @context.subst_method
    def doc_relocation (self):
        return misc.join_lines ('''
LILYPOND_EXTERNAL_BINARY=%(system_prefix)s/bin/lilypond
PATH=%(tools_prefix)s/bin:%(system_prefix)s/bin:$PATH
GS_LIB=%(system_prefix)s/share/ghostscript/*/lib
MALLOC_CHECK_=2
LD_LIBRARY_PATH=%(tools_prefix)s/lib:%(system_prefix)s/lib:${LD_LIBRARY_PATH-/foe}
''')
    def force_sequential_build (self):
        '''
Writing snippets...
All snippets are up to date...lilypond-book.py (GNU LilyPond) 2.12.3
Traceback (most recent call last):
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 2107, in ?
    main ()
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 2089, in main
    chunks = do_file (files[0])
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 1993, in do_file
    do_process_cmd (chunks, input_fullname, global_options)
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 1844, in do_process_cmd
    options.output_dir)
  File "/home/janneke/vc/gub/target/linux-64/src/lilypond-git.sv.gnu.org--lilypo
nd.git-master/scripts/lilypond-book.py", line 1278, in link_all_output_files
    os.makedirs (dst_path)
  File "/home/janneke/vc/gub/target/tools/root/usr/lib/python2.4/os.py", line 15
9, in makedirs
    mkdir(name, mode)
OSError: [Errno 17] File exists: '/home/janneke/vc/gub/target/linux-64/build/lil
ypond-git.sv.gnu.org--lilypond.git-master/Documentation/user/out/6a'
'''
        return True
    def compile_command (self):
        return ('%(doc_limits)s '
                '&& %(doc_relocation)s '
                + target.AutoBuild.compile_command (self))
    def install_command (self):
        return ('%(doc_limits)s '
                '&& %(doc_relocation)s '
                + target.AutoBuild.install_command (self))

Lilypond_base = LilyPond_base

#Hmm
Lilypond = LilyPond
Lilypond__cygwin = LilyPond__cygwin
Lilypond__darwin = LilyPond__darwin
Lilypond__darwin__ppc = LilyPond__darwin__ppc
Lilypond__debian = LilyPond__debian
Lilypond__mingw = LilyPond__mingw
Lilypond__debian_arm = LilyPond__debian
Lilypond__mipsel = LilyPond__debian
