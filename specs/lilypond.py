import os
import re
#
import cvs
import repository
import gub
import misc
import targetpackage


from context import *

class LilyPond (targetpackage.TargetBuildSpec):
    '''A program for printing sheet music
LilyPond lets you create music notation.  It produces
beautiful sheet music from a high-level description file.'''

    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)


        try:
            source = os.environ['GUB_LILYPOND_SOURCE']
        except KeyError:         
            source = 'git://git.sv.gnu.org/lilypond.git'
        
        if 'pserver' in source:
            repo = repository.CVSRepository (
                self.get_repodir (),
                source=':pserver:anoncvs@cvs.sv.gnu.org:/cvsroot/lilypond',
                module='lilypond',
                tag=settings.lilypond_branch)
        else:
            repo = repository.GitRepository (
                self.get_repodir (),
                branch=settings.lilypond_branch,
                source=source)

        ## ugh: nested, with self shadow?
        def version_from_VERSION (self):
            s = self.get_file_content ('VERSION')
            d = misc.grok_sh_variables_str (s)
            v = '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
            return v

        from new import instancemethod
        repo.version = instancemethod (version_from_VERSION, repo, type (repo))

        self.with_vc (repo)

        # FIXME: should add to C_INCLUDE_PATH
        builddir = self.builddir ()
        self.target_gcc_flags = (settings.target_gcc_flags
                                 + ' -I%(builddir)s' % locals ())

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
    
    def broken_for_distcc (self):
        ## mf/ is broken
        return True

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
        c = targetpackage.TargetBuildSpec.rsync_command (self)
        c = c.replace ('rsync', 'rsync --delete --exclude configure')
        return c

    def configure_command (self):
        ## FIXME: pickup $target-guile-config
        return (targetpackage.TargetBuildSpec.configure_command (self)
                + misc.join_lines ('''
--enable-relocation
--disable-documentation
--enable-static-gxx
--with-ncsb-dir=%(system_root)s/usr/share/fonts/default/Type1
'''))

    def configure (self):
        self.autoupdate ()

    def do_configure (self):
        if not os.path.exists (self.expand ('%(builddir)s/FlexLexer.h')):
            flex = self.read_pipe ('which flex')
            flex_include_dir = os.path.split (flex)[0] + "/../include"
            self.system ('''
mkdir -p %(builddir)s
cp %(flex_include_dir)s/FlexLexer.h %(builddir)s/
''', locals ())
            
        self.config_cache ()
        self.system ('''
mkdir -p %(builddir)s 
cd %(builddir)s && %(configure_command)s''')
        self.file_sub ([(' -O2 ', ' -O2 -Werror ')],
                       '%(builddir)s/config.make')

    def compile (self):
        d = self.get_substitution_dict ()
        if (misc.file_is_newer ('%(srcdir)s/config.make.in' % d,
                                '%(builddir)s/config.make' % d)
            or misc.file_is_newer ('%(srcdir)s/GNUmakefile.in' % d,
                                   '%(builddir)s/GNUmakefile' % d)
            or misc.file_is_newer ('%(srcdir)s/config.hh.in' % d,
                                   '%(builddir)s/config.hh' % d)
            or misc.file_is_newer ('%(srcdir)s/configure' % d,
                                   '%(builddir)s/config.make' % d)):

            self.do_configure ()
            self.system ('touch %(builddir)s/config.hh')
            
        targetpackage.TargetBuildSpec.compile (self)

    def name_version (self):
        # FIXME: make use of branch for version explicit, use
        # name-branch for src /build dir, use name-version for
        # packaging.
        try:
            return self.build_version ()
        except:
            return targetpackage.TargetBuildSpec.name_version (self)

    def build_version (self):
        d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
        v = '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
        return v

    def build_number (self):
        import versiondb
        db = versiondb.VersionDataBase (self.settings.lilypond_versions)
        v = tuple (map (int, self.build_version ().split ('.')))
        b = db.get_next_build_number (v)
        return ('%d' % b)

    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        # FIXME: This should not be in generic package, for installers only.
        self.installer_install_stuff ()

    def installer_install_stuff (self):
        # FIXME: is it really the installer version that we need here,
        # or do we need the version of lilypond?
        installer_version = self.build_version ()
        # WTF, current.
        self.system ("cd %(install_root)s/usr/share/lilypond && mv %(installer_version)s current",
                     locals ())

        self.system ("cd %(install_root)s/usr/lib/lilypond && mv %(installer_version)s current",
                     locals ())

        self.system ('mkdir -p %(install_root)s/usr/etc/fonts/')
        fc_conf_file = open (self.expand ('%(install_root)s/usr/etc/fonts/local.conf'), 'w')
        fc_conf_file.write ('''
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
''' % locals ())

    def gub_name (self):
        nv = self.name_version ()
        p = self.settings.platform
        return '%(nv)s.%(p)s.gub' % locals ()

    def autoupdate (self, autodir=0):
        autodir = self.srcdir ()

        if (misc.file_is_newer (self.expand ('%(autodir)s/configure.in', locals ()),
                                self.expand ('%(builddir)s/config.make',locals ()))
            or misc.file_is_newer (self.expand ('%(autodir)s/stepmake/aclocal.m4', locals ()),
                                   self.expand ('%(autodir)s/configure', locals ()))):
            self.system ('''
            cd %(autodir)s && bash autogen.sh --noconfigure
            ''', locals ())
            self.do_configure ()

class LilyPond__cygwin (LilyPond):

    def get_subpackage_names (self):
        return ['doc', '']

    def get_dependency_dict (self):
        return {
            '' :
            [
            'glib2',
            'guile-runtime',
            'libfontconfig1',
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
            'libfontconfig-devel',
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
        return LilyPond.configure_command (self).replace ('--enable-relocation',
                                                          '--disable-relocation')

    def compile (self):
        self.system ('''
        cp -pv %(system_root)s/usr/share/gettext/gettext.h %(system_root)s/usr/include''')
        LilyPond.compile (self)

    def compile_command (self):
        ## UGH - * sucks.
        python_lib = "%(system_root)s/usr/bin/libpython*.dll"
        LDFLAGS = '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api'

        ## UGH. 
        return (LilyPond.compile_command (self)
                + misc.join_lines ('''
LDFLAGS="%(LDFLAGS)s %(python_lib)s"
'''% locals ()))

    def install (self):
        ##LilyPond.install (self)
        targetpackage.TargetBuildSpec.install (self)
        self.install_doc ()

    def install_doc (self):
        installer_build = self.build_number ()
        installer_version = self.build_version ()
        docball = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.documentation.tar.bz2', env=locals ())
        infomanball = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.info-man.tar.bz2', env=locals ())
        if not os.path.exists (docball):
            # Must not have cygwin CC, CXX settings.
            os.system ('''make doc''')
        self.system ('''
mkdir -p %(install_root)s/usr/share/doc/lilypond
tar -C %(install_root)s/usr/share/doc/lilypond -jxf %(docball)s
tar -C %(install_root)s -jxf %(infomanball)s
find %(install_root)s/usr/share/doc/lilypond -name '*.signature' -exec rm '{}' ';'
find %(install_root)s/usr/share/doc/lilypond -name '*.ps' -exec rm '{}' ';'
mkdir -p %(install_root)s/usr/share/info/lilypond
cd %(install_root)s/usr/share/info/lilypond && ln -sf ../../doc/lilypond/Documentation/user/*png .
''',
                  locals ())

    def category_dict (self):
        return {'': 'publishing', 'doc': 'doc'}

    def description_dict (self):
        # FIXME: fairly uninformative description for packages,
        # unlike, eg, guile-devel.  This is easier, though.
        d = {}
        for i in self.get_subpackage_names ():
            d[i] = self.get_subpackage_doc (i)
        return d

    def get_subpackage_doc (self, split):
        flavor = {'': 'executables', 'doc': 'documentation'}[split]
        return (LilyPond.__doc__.replace ('\n', ' - %(flavor)s\n', 1)
                % locals ())
        
class LilyPond__freebsd (LilyPond):
    def get_dependency_dict (self):
        d = LilyPond.get_dependency_dict (self)
        d[''].append ('gcc')
        return d

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
        python_lib = "%(system_root)s/usr/bin/libpython*.dll"
        LDFLAGS = '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api'

        ## UGH. 
        return (LilyPond.compile_command (self)
                + misc.join_lines ('''
LDFLAGS="%(LDFLAGS)s %(python_lib)s"
'''% locals ()))
    
    def do_configure (self):
        LilyPond.do_configure (self)

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
cp %(install_root)s/usr/lib/lilypond/*/python/* %(install_root)s/usr/bin
cp %(install_root)s/usr/share/lilypond/*/python/* %(install_root)s/usr/bin
''')
        import glob
        for i in glob.glob (self.expand ('%(install_root)s/usr/bin/*')):
            s = self.read_pipe ('file %(i)s' % locals ())
            if s.find ('guile') >= 0:
                self.system ('mv %(i)s %(i)s.scm', locals ())
            elif s.find ('python') >= 0 and not i.endswith ('.py'):
                self.system ('mv %(i)s %(i)s.py', locals ())

        for i in self.locate_files ('%(install_root)s', "*.ly"):
            s = open (i).read ()
            open (i, 'w').write (re.sub ('\r*\n', '\r\n', s))


## please document exactly why if this is switched back.
#        self.file_sub ([(r'gs-font-load\s+#f', 'gs-font-load #t')],
#        '%(install_root)s/usr/share/lilypond/current/scm/lily.scm')

class LilyPond__debian (LilyPond):
    def get_dependency_dict (self):
        import debian, gup
        return {'': gup.gub_to_distro_deps (LilyPond.get_dependency_dict (self)[''],
                                            debian.gub_to_distro_dict)}

    def install (self):
        targetpackage.TargetBuildSpec.install (self)

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

##
class LilyPond__darwin (LilyPond):
    def get_dependency_dict (self):
        d = LilyPond.get_dependency_dict (self)

        deps = d['']
        deps.remove ('python-runtime')
        deps += [ 'fondu', 'osx-lilypad']

        d[''] = deps
        return d

    def get_build_dependencies (self):
        return LilyPond.get_build_dependencies (self) + [ 'fondu', 'osx-lilypad']

    def compile_command (self):
        return LilyPond.compile_command (self) + " TARGET_PYTHON=/usr/bin/python "
    
    def configure_command (self):
        cmd = LilyPond.configure_command (self)
        cmd += ' --enable-static-gxx '

        return cmd

    def do_configure (self):
        LilyPond.do_configure (self)

        make = self.expand ('%(builddir)s/config.make')

        if re.search ("GUILE_ELLIPSIS", open (make).read ()):
            return
        self.file_sub ([('CONFIG_CXXFLAGS = ',
                         'CONFIG_CXXFLAGS = -DGUILE_ELLIPSIS=... '),

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
Lilypond__freebsd = LilyPond__freebsd
Lilypond__arm = LilyPond__debian
Lilypond__mipsel = LilyPond__debian
