import os
import re
#
import cvs
import gub
import misc
import targetpackage


from context import *

class LilyPond (targetpackage.TargetBuildSpec):
    def get_dependency_dict (self):
        return {'': ['fontconfig', 'gettext', 
                     'guile', 'pango', 'python',
                     'ghostscript']}

    def get_subpackage_names (self):
        return ['']
    
    def broken_for_distcc (self):

        ## mf/ is broken
        return True
    def get_build_dependencies (self):
        return ['guile-devel', 'python-devel', 'fontconfig-devel',

                ## not really true, but makes our GNUmakefile more difficult otherwise 
                'ghostscript',
                'gettext-devel',  'pango-devel', 'freetype-devel', 'urw-fonts']

    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
                   track_development=True)

        # FIXME: should add to C_INCLUDE_PATH
        builddir = self.builddir ()
        self.target_gcc_flags = (settings.target_gcc_flags
                    + ' -I%(builddir)s' % locals ())
        self._downloader = self.cvs

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

    # FIXME: shared for all CVS packages
    def srcdir (self):
        return '%(allsrcdir)s/%(name)s-%(version)s'

#        # FIXME: shared for all CVS packages
    def builddir (self):
        return '%(targetdir)s/build/%(name)s-%(version)s'

    def compile (self):
        d = self.get_substitution_dict ()
        if (misc.file_is_newer ('%(srcdir)s/config.make.in' % d,
                 '%(builddir)s/config.make' % d)
          or misc.file_is_newer ('%(srcdir)s/GNUmakefile.in' % d,
                   '%(builddir)s/GNUmakefile' % d)
          or misc.file_is_newer ('%(srcdir)s/config.hh.in' % d,
                   '%(builddir)s/config.make' % d)
          or misc.file_is_newer ('%(srcdir)s/configure' % d,
                   '%(builddir)s/config.make' % d)):
            self.do_configure ()

        targetpackage.TargetBuildSpec.compile (self)

    def name_version (self):
        # FIXME: make use of branch for version explicit, use
        # name-branch for src /build dir, use name-version for
        # packaging.
        try:
            self.build_version ()
        except:
            return targetpackage.TargetBuildSpec.name_version (self)

    def build_version (self):
        d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
        v = '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
        return v

    def build_number (self):
        build_number_file = '%(topdir)s/buildnumber-%(lilypond_branch)s.make'
        d = misc.grok_sh_variables (self.expand (build_number_file))
        b = '%(INSTALLER_BUILD)s' % d
        return b

    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        # FIXME: This should not be in generic package, for installers only.
        self.installer_install_stuff ()

    def installer_install_stuff (self):
        # FIXME: is it really the installer version that we need here,
        # or do we need the version of lilypond?
        installer_version = build_version ()
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

<cache>~/.lilypond-%(installer_version)s-font.cache-1</cache>
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
    def __init__ (self, settings):
        LilyPond.__init__ (self, settings)
        self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
                   track_development=True)

    def get_subpackage_names (self):
        return ['doc', '']
    
    def get_dependency_dict (self):
        return {'' : [
            'glib2', 'libfontconfig1', 'libfreetype26',
            #'libguile17', #cygwin name
            'guile-libguile17', #gub name
            'libiconv', 'pango-runtime', 'python'
            ]}

    def get_build_dependencies (self):
        return ['gettext-devel', 'glib2-devel',
                #'guile-devel',
                'guile',
                'python',
                'libfontconfig-devel', 'libfreetype2-devel', 'pango-devel',
                'urw-fonts']

    def get_distro_dependency_dict (self):
        return {
            'lilypond' : ['bash', 'coreutils', 'cygwin', 'findutils',
                          'ghostscript', 'glib2-runtime', 'libfontconfig1',
                          'libfreetype26', 'libguile17', 'libiconv2', 'libintl3',
                          'pango-runtime', 'python', '_update-info-dir'],
            'lilypond-doc' : []
            }

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
        import cygwin
        cygwin.dump_readme_and_hints (self)
        cygwin.copy_readmes_buildspec (self)
        cygwin.cygwin_patches_dir_buildspec (self)

        self.install_doc ()

    def install_doc (self):
        installer_build = self.build_number ()
        installer_version = self.build_version ()
        docball = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.documentation.tar.bz2', env=locals ())
        if not os.path.exists (docball):
            # Must not have cygwin CC, CXX settings.
            os.system ('''make doc''')
        self.system ('''
mkdir -p %(install_root)s/usr/share/doc/lilypond
tar -C %(install_root)s/usr/share/doc/lilypond -jxf %(docball)s
''',
                  locals ())

class LilyPond__freebsd (LilyPond):
    def __init__ (self, settings):
        LilyPond.__init__ (self, settings)
    def get_dependency_dict (self):
        d = LilyPond.get_dependency_dict (self)
        d[''].append ('gcc')
        return d

class LilyPond__mingw (LilyPond):
    def __init__ (self, settings):
        LilyPond.__init__ (self, settings)
        self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
                   track_development=True)
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
        LilyPond.compile (self)
        self.system ('cd %(builddir)s/lily && mv out/lilypond out/lilypond-console')
        self.system ('cd %(builddir)s/lily && make MODULE_LDFLAGS="-mwindows"')

    def install (self):
        LilyPond.install (self)
        self.system ('''
rm -f %(install_prefix)s/bin/lilypond-windows
install -m755 %(builddir)s/lily/out/lilypond %(install_prefix)s/bin/lilypond-windows.exe
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
    def __init__ (self, settings):
        LilyPond.__init__ (self, settings)
        self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
                   track_development=True)

    def install (self):
        targetpackage.TargetBuildSpec.install (self)

    def get_build_dependencies (self):
        return [
            'gettext',
            'guile-1.6-dev',
            'libfontconfig1-dev',
            'libfreetype6-dev',
            'libglib2.0-dev',
            'python2.4-dev',
            'libpango1.0-dev',
            'zlib1g-dev',
            ]

##
class LilyPond__darwin (LilyPond):
    def __init__ (self, settings):
        LilyPond.__init__ (self, settings)
        self.with (version=settings.lilypond_branch,
                   mirror=cvs.gnu,
                   track_development=True)

    def get_dependency_dict (self):
        d = LilyPond.get_dependency_dict (self)
        d[''] += [ 'fondu', 'osx-lilypad']
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
Lilypond__mipsel = LilyPond__debian
