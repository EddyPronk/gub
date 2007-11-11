import os
import re
#
from gub import repository
from gub import build
from gub import misc
from gub import targetbuild
from gub import commands

class LilyPond (targetbuild.TargetBuild):
    source = 'git://git.sv.gnu.org/lilypond.git'
    download_before_init = True
    need_source_tree = True
    branch = 'master'

    '''A program for printing sheet music
LilyPond lets you create music notation.  It produces
beautiful sheet music from a high-level description file.'''

    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        if os.environ.has_key ('GUB_LILYPOND_SOURCE'):
            raise 'Just use generic feature: bin/gub -p %(platform)s $GUB_LILYPOND_SOURCE' % settings.__dict__

        # FIXME: should add to C_INCLUDE_PATH
        builddir = self.builddir ()
        self.target_gcc_flags = (settings.target_gcc_flags
                                 + ' -I%(builddir)s' % locals ())

        ## ugh: nested, with self shadow?
        def version_from_VERSION (self):
            s = self.read_file ('VERSION')
            d = misc.grok_sh_variables_str (s)
            v = '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d

            return v

        from new import instancemethod
        if isinstance (source, repository.Repository):
            source.version = instancemethod (version_from_VERSION, source, type (source))

    def get_dependency_dict (self):
        return {'': [
            'fontconfig',
            'gettext', 
            'guile-runtime',
            'pango',
            'python-runtime',
            'ghostscript'
            ]}
    
    def get_subpackage_names (self):
        return ['']
    
    def get_build_dependencies (self):
        return ['fontconfig-devel',
                'freetype-devel',
                'gettext-devel',
                'ghostscript',
                'guile-devel',
                'pango-devel',
                'python-devel',
                'urw-fonts']

    def rsync_command (self):
        c = targetbuild.TargetBuild.rsync_command (self)
        c = c.replace ('rsync', 'rsync --delete --exclude configure')
        return c
    def stages (self):
        return misc.list_insert_before (targetbuild.TargetBuild.stages (self),
                                        'configure', 'autoupdate')
    def autoupdate (self):
        # FIXME: why do we need a specific lilypond kludge.  can't
        # this be done more generically?  shouldn't we check on
        # source.is_tracking?
        def must_autogen ():
            return (self.first_is_newer ('%(srcdir)s/configure.in',
                                         '%(builddir)s/config.make')
                    or self.first_is_newer ('%(srcdir)s/stepmake/aclocal.m4',
                                            '%(srcdir)s/configure'))
        self.runner.pred_if_else (must_autogen, commands.System (self.expand ('cd %(srcdir)s && bash autogen.sh --noconfigure')))

    def configure_command (self):
        ## FIXME: pickup $target-guile-config
        return (targetbuild.TargetBuild.configure_command (self)
                + misc.join_lines ('''
--enable-relocation
--disable-documentation
--enable-static-gxx
--with-ncsb-dir=%(system_prefix)s/share/fonts/default/Type1
'''))

    def configure (self):
        # FIXME: why do we need a specific lilypond kludge.  can't
        # this be done more genericly?  shouldn't we check on
        # source.is_tracking?
        def must_reconfigure ():
            return (self.first_is_newer ('%(srcdir)s/config.make.in',
                                         '%(builddir)s/config.make')
                    or self.first_is_newer ('%(srcdir)s/GNUmakefile.in',
                                            '%(builddir)s/GNUmakefile')
                    or self.first_is_newer ('%(srcdir)s/config.hh.in',
                                            '%(builddir)s/config.hh')
                    or self.first_is_newer ('%(srcdir)s/configure',
                                            '%(builddir)s/config.make')
                    ## need to reconfigure if dirs were added.
                    or (len (self.locate_files ('%(builddir)s', 'GNUmakefile'))
                        != len (self.locate_files ('%(srcdir)s', 'GNUmakefile')) + 1))
        self.runner.pred_if_else (must_reconfigure,
                                  commands.Func (self.reconfigure))

    def reconfigure (self):
        if not os.path.exists (self.expand ('%(builddir)s/FlexLexer.h')):
            flex = self.read_pipe ('which flex')
            flex_include_dir = os.path.split (flex)[0] + '/../include'
            self.system ('''
mkdir -p %(builddir)s
cp %(flex_include_dir)s/FlexLexer.h %(builddir)s
''', locals ())
        self.config_cache ()
        targetbuild.TargetBuild.configure (self)
        self.system ('touch %(builddir)s/config.hh')
        self.file_sub ([(' -O2 ', ' -O2 -Werror ')], '%(builddir)s/config.make')

    def compile (self):
        self.configure ()
        targetbuild.TargetBuild.compile (self)

    def name_version (self):
        return targetbuild.TargetBuild.name_version (self)

    def build_version (self):
        d = misc.grok_sh_variables_str (self.source.read_file ('VERSION'))
        v = '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
        self.runner.info ('LILYPOND-VERSION: %(v)s\n' % locals ())
        return v

    def pretty_name (self):
        return 'LilyPond'
    
    def install (self):
        targetbuild.TargetBuild.install (self)
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

    def get_dependency_dict (self):
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

    def get_build_dependencies (self):

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
            'fontconfig', ## CYGWIN: 'libfontconfig-devel',
            ##'freetype2', ## CYGWIN: 'libfreetype2-devel',
            'libfreetype2-devel',
            # cygwin bug: pango-devel should depend on glib2-devel
            'pango-devel', 'glib2-devel',
            'urw-fonts'] + [
            'bash',
            'coreutils',
            'findutils',
            'ghostscript',
            ]

    def configure_command (self):
        return (LilyPond.configure_command (self)
                .replace ('--enable-relocation', '--disable-relocation'))

    def compile (self):
	# Because of relocation script, python must be built before scripts
        # PYTHON= is replaces the detected python interpreter in tools.
        self.system ('''
cd %(builddir)s && make -C python LDFLAGS=%(system_prefix)s/bin/libpython*.dll
cd %(builddir)s && make -C scripts PYTHON=/usr/bin/python
cp -pv %(system_prefix)s/share/gettext/gettext.h %(system_prefix)s/include''')
        LilyPond.compile (self)

    def compile_command (self):
        ## UGH - * sucks.
        python_lib = '%(system_prefix)s/bin/libpython*.dll'
        LDFLAGS = '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api'

        ## UGH. 
        return (LilyPond.compile_command (self)
                + misc.join_lines ('''
LDFLAGS="%(LDFLAGS)s %(python_lib)s"
'''% locals ()))

    def install (self):
        ##LilyPond.install (self)
        targetbuild.TargetBuild.install (self)
        self.install_doc ()

    def install_doc (self):
        # lilypond.make uses `python gub/versiondb.py --build-for=2.11.32'
        # which only looks at source ball build numbers, which are always `1'
        # This could be fixed, but for now just build one doc ball per release?
        installer_build = '1'
        installer_version = self.build_version ()
        docball = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.documentation.tar.bz2', env=locals ())
        infomanball = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.info-man.tar.bz2', env=locals ())

        if not os.path.exists (docball):
            ## can't run make, because we need the right variables (BRANCH, etc.)
            raise Exception ('cannot find docball %s' % docball)
            
        self.system ('''
mkdir -p %(install_prefix)s/share/doc/lilypond
tar -C %(install_prefix)s/share/doc/lilypond -jxf %(docball)s
tar -C %(install_root)s -jxf %(infomanball)s
find %(install_prefix)s/share/doc/lilypond -name '*.signature' -exec rm '{}' ';'
find %(install_prefix)s/share/doc/lilypond -name '*.ps' -exec rm '{}' ';'
mkdir -p %(install_prefix)s/share/info/lilypond
cd %(install_prefix)s/share/info/lilypond && ln -sf ../../doc/lilypond/Documentation/user/*png .
''',
                  locals ())

    def category_dict (self):
        return {'': 'Publishing'}

## shortcut: take python out of dependencies
class LilyPond__no_python (LilyPond):
    def get_build_dependencies (self):
        d = LilyPond.get_build_dependencies (self)
        d.remove ('python-devel')
        return d

    def get_dependency_dict (self):
        d = LilyPond.get_dependency_dict (self)
        d[''].remove ('python-runtime')
        return d

    def configure (self):
        self.system ('mkdir -p %(builddir)s', ignore_errors=True) 
        self.system ('touch %(builddir)s/Python.h') 
        LilyPond.configure (self)
        self.dump ('''
all:
	true

install:
	-mkdir -p $(DESTDIR)%(prefix_dir)s/lib/lilypond/%(version)s
''', '%(builddir)s/python/GNUmakefile')
        
class LilyPond__mingw (LilyPond):
    def get_dependency_dict (self):
        d = LilyPond.get_dependency_dict (self)
        d[''].append ('lilypad')        
        return d

    def get_build_dependencies (self):
        return LilyPond.get_build_dependencies (self) + ['lilypad']

    ## ugh c&p
    def compile_command (self):

        ## UGH - * sucks.
        python_lib = '%(system_prefix)s/bin/libpython*.dll'
        LDFLAGS = '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api'

        ## UGH. 
        return (LilyPond.compile_command (self)
                + misc.join_lines ('''
LDFLAGS="%(LDFLAGS)s %(python_lib)s"
'''% locals ()))
    
    def configure (self):
        LilyPond.configure (self)

        ## huh, why ? --hwn
        self.config_cache ()

        ## for console: no -mwindows
        self.file_sub ([(' -mwindows', ' '),

                ## gdb doesn't work on windows anyway.
                (' -g ', ' '),
                ],
               '%(builddir)s/config.make')

    def compile (self):
        self.system ('cd %(builddir)s/lily && rm -f out/lilypond', ignore_errors=True)
        LilyPond.compile (self)
        self.system ('cd %(builddir)s/lily && mv out/lilypond out/lilypond-console')
        self.system ('cd %(builddir)s/lily && make MODULE_LDFLAGS="-mwindows" && mv out/lilypond out/lilypond-windows')
        self.system ('cd %(builddir)s/lily && touch out/lilypond')

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
        import glob
        for i in glob.glob (self.expand ('%(install_prefix)s/bin/*')):
            header = open (i).readline().strip ()
            if header.endswith ('guile'):
                self.system ('mv %(i)s %(i)s.scm', locals ())
            elif header.endswith ('python') and not i.endswith ('.py'):
                self.system ('mv %(i)s %(i)s.py', locals ())

        for i in self.locate_files ('%(install_root)s', '*.ly'):
            s = open (i).read ()
            open (i, 'w').write (re.sub ('\r*\n', '\r\n', s))

        bat = r'''@echo off
"@INSTDIR@\usr\bin\lilypond-windows.exe" -dgui %1 %2 %3 %4 %5 %6 %7 %8 %9
'''.replace ('%', '%%').replace ('\n', '\r\n')
            
        self.dump (bat, '%(install_prefix)s/bin/lilypond-windows.bat.in')

## please document exactly why if this is switched back.
#        self.file_sub ([(r'gs-font-load\s+#f', 'gs-font-load #t')],
#        '%(install_prefix)s/share/lilypond/current/scm/lily.scm')

class LilyPond__debian (LilyPond):
    def get_dependency_dict (self):
        from gub import debian, gup
        return {'': gup.gub_to_distro_deps (LilyPond.get_dependency_dict (self)[''],
                                            debian.gub_to_distro_dict)}

    def compile (self):
	# Because of relocation script, python must be built before scripts
        self.system ('''
cd %(builddir)s && make -C python
cd %(builddir)s && make -C scripts PYTHON=/usr/bin/python
''')
        LilyPond.compile (self)

    def install (self):
        targetbuild.TargetBuild.install (self)

    def get_build_dependencies (self):
        #FIXME: aargh, MUST specify gs,  etc here too.
        return [
            'gettext',
            'guile-1.6-dev',
            'libfontconfig1-dev',
            'libfreetype6-dev',
            'libglib2.0-dev',
            'python2.4-dev',
            'libpango1.0-dev',
            'zlib1g-dev',
            'urw-fonts',
            ] + ['gs']


class LilyPond__darwin (LilyPond):
    def get_dependency_dict (self):
        d = LilyPond.get_dependency_dict (self)
        deps = d['']
        deps.remove ('python-runtime')
        deps += [ 'fondu', 'osx-lilypad']
        d[''] = deps
        return d

    def get_build_dependencies (self):
        return (LilyPond.get_build_dependencies (self)
                + [ 'fondu', 'osx-lilypad'])

    def compile_command (self):
        return (LilyPond.compile_command (self)
                + ' TARGET_PYTHON=/usr/bin/python')
    
    def configure_command (self):
        return (LilyPond.configure_command (self)
                + ' --enable-static-gxx')

    def configure (self):
        LilyPond.configure (self)
        make = self.expand ('%(builddir)s/config.make')
        self.file_sub ([('CONFIG_CXXFLAGS = ',
                         'CONFIG_CXXFLAGS =-DGUILE_ELLIPSIS=... '),
## optionally: switch off for debugging.
#                                (' -O2 ', '')
                ],
               '%(builddir)s/config.make')

#Hmm
Lilypond = LilyPond
Lilypond__cygwin = LilyPond__cygwin
Lilypond__darwin = LilyPond__darwin
Lilypond__debian = LilyPond__debian
Lilypond__mingw = LilyPond__mingw
Lilypond__freebsd = LilyPond
Lilypond__debian_arm = LilyPond__debian
Lilypond__mipsel = LilyPond__debian
