import glob
import os
import re
import shutil

import cvs
import gub
import misc
import targetpackage

class LilyPond (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
             depends=['fontconfig', 'gettext',
                  'guile', 'pango', 'python', 'ghostscript'],
             track_development=True)

        # FIXME: should add to C_INCLUDE_PATH
        builddir = self.builddir ()
        self.target_gcc_flags = (settings.target_gcc_flags
                    + ' -I%(builddir)s' % locals ())
        self._downloader = self.cvs

    def rsync_command (self):
        c = targetpackage.Target_package.rsync_command (self)
        c = c.replace ('rsync', 'rsync --delete --exclude configure')
        return c

    def configure_command (self):
        ## FIXME: pickup $target-guile-config
        return (targetpackage.Target_package.configure_command (self)

                ## UGH: fixme: hardcoded font path.
            + misc.join_lines ('''
--enable-relocation
--disable-documentation
--enable-ncsb-path=/usr/share/fonts/default/Type1/
--enable-static-gxx
--with-python-include=%(system_root)s/usr/include/python%(python_version)s
'''))

    def configure (self):
        self.autoupdate ()


    def do_configure (self):
        if not os.path.exists (self.expand ('%(builddir)s/FlexLexer.h')):
            flex = self.read_pipe ('which flex')
            flex_include_dir = os.path.split (flex)[0] + "/../include"
            gub.Package.system (self, '''
mkdir -p %(builddir)s
cp %(flex_include_dir)s/FlexLexer.h %(builddir)s/
''', locals ())
        targetpackage.Target_package.configure (self)

        self.file_sub ([('DEFINES = ', r'DEFINES = -DGHOSTSCRIPT_VERSION=\"%(ghostscript_version)s\" ')],
               '%(builddir)s/config.make')

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

        targetpackage.Target_package.compile (self)

    def compile_command (self):
        s = targetpackage.Target_package.compile_command (self)
        if self.settings.lilypond_branch == 'lilypond_2_6':
            # ugh, lilypond-2.6 has broken srcdir build system
            # and gub is leaking all kind of vars.
            s = 'unset builddir srcdir topdir;' + s

        return s

    def name_version (self):
        # whugh
        if os.path.exists (self.srcdir ()):
            d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
            return 'lilypond-%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
        return targetpackage.Target_package.name_version (self)

    def install (self):
        targetpackage.Target_package.install (self)
        d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
        v = '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
        # WTF, current?
        self.system ("cd %(install_root)s/usr/share/lilypond && mv %(v)s current",
              locals ())

        self.system ("cd %(install_root)s/usr/lib/lilypond && mv %(v)s current",
              locals ())

        self.system ('mkdir -p %(install_root)s/usr/etc/fonts/')
        fc_conf_file = open (self.expand ('%(install_root)s/usr/etc/fonts/local.conf'), 'w')
        fc_conf_file.write ('''
<selectfont>
 <rejectfont>
 <pattern>
  <patelt name="scalable"><bool>false</bool></patelt>
 </pattern>
 </rejectfont>
</selectfont>

<cache>~/.lilypond-%(v)s-font.cache-1</cache>''' % locals ())



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
             depends=['fontconfig', 'freetype2', 'gettext', 'glib2', 'guile', 'libiconv', 'pango', 'python'],
             builddeps=['gettext-devel', 'glib2-devel', 'guile', 'libfontconfig-devel', 'libfreetype2-devel', 'libiconv', 'pango-devel', 'python'],
             track_development=True)
        self.split_packages = ['doc']

    def patch (self):
        # FIXME: for our gcc-3.4.5 cross compiler in the mingw
        # environment, THIS is a magic word.
        self.file_sub ([('THIS', 'SELF')],
               '%(srcdir)s/lily/parser.yy')

    def compile_command (self):
        python_lib = "%(system_root)s/usr/bin/libpython%(python_version)s.dll"
        LDFLAGS = '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api'

        return (LilyPond.compile_command (self)
           + misc.join_lines ('''
LDFLAGS="%(LDFLAGS)s %(python_lib)s"
'''% locals ()))

    #URG guile.py c&p
    def install (self):
        targetpackage.Target_package.install (self)
        self.system ('''
mkdir -p %(install_root)s/usr/share/doc/lilypond
cp -prv %(srcdir)s/input %(install_root)s/usr/share/doc/lilypond
''')
        self.dump_readme_and_hints ()
        self.copy_readmes ()
        # Hmm, is this really necessary?
        cygwin_patches = '%(srcdir)s/CYGWIN-PATCHES'
        self.system ('''
mkdir -p %(cygwin_patches)s
cp -pv %(install_root)s/etc/hints/* %(cygwin_patches)s
cp -pv %(install_root)s/usr/share/doc/Cygwin/* %(cygwin_patches)s
''',
              locals ())

    #URG guile.py c&p
    def copy_readmes (self):
        self.system ('''
mkdir -p %(install_root)s/usr/share/doc/%(name)s
''')
        for i in glob.glob ('%(srcdir)s/[A-Z]*'
                  % self.get_substitution_dict ()):
            if (os.path.isfile (i)
              and not i.startswith ('Makefile')
              and not i.startswith ('GNUmakefile')):
                shutil.copy2 (i, '%(install_root)s/usr/share/doc/%(name)s' % self.get_substitution_dict ())

    def dump_readme_and_hints (self):
        # FIXME: get depends from actual split_packages
        changelog = open (self.settings.sourcefiledir + '/lilypond.changelog').read ()
        self.system ('''
mkdir -p %(install_root)s/usr/share/doc/Cygwin
mkdir -p %(install_root)s/etc/hints
''')

        readme = open (self.settings.sourcefiledir + '/lilypond.README').read ()
        self.dump (readme,
             '%(install_root)s/usr/share/doc/Cygwin/%(name)s-%(bundle_version)s-%(bundle_build)s.README',
             env=locals ())

        fixdepends = {
            'lilypond' : ['bash', 'coreutils', 'cygwin', 'findutils', 'ghostscript', 'glib2-runtime', 'libfontconfig1', 'libfreetype26', 'libguile17', 'libiconv2', 'libintl3', 'pango-runtime', 'python', '_update-info-dir'],
            'lilypond-doc' : []
            }

        for name in ['lilypond', 'lilypond-doc']:
            depends = fixdepends[name]
            requires = ' '.join (depends)
            hint = self.expand (open (self.settings.sourcefiledir + '/' + name + '.hint').read (), locals ())
            self.dump (hint,
                 '%(install_root)s/etc/hints/%(name)s.hint',
                 env=locals ())

    def split_doc (self):
        docball = self.expand ('%(uploads)s/lilypond-%(bundle_version)s-%(bundle_build)s.documentation.tar.bz2')
        if not os.path.exists (docball):
            # Must not have cygwin CC, CXX settings.
            os.system ('''make doc''')
        self.system ('''
mkdir -p %(install_root)s/usr/share/doc/lilypond
tar -C %(install_root)s/usr/share/doc/lilypond -jxf %(docball)s
''',
                  locals ())
        LilyPond.split_doc (self)

class LilyPond__freebsd (LilyPond):
    def __init__ (self, settings):
        LilyPond.__init__ (self, settings)

        # libgcc.so
        self.name_dependencies.append ('gcc')

class LilyPond__mingw (LilyPond__cygwin):
    def __init__ (self, settings):
        LilyPond__cygwin.__init__ (self, settings)
        self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
             depends=['fontconfig', 'gettext',
                  'guile', 'pango', 'python', 'ghostscript', 'lilypad'],
             track_development=True)
        self.split_packages = []

    def do_configure (self):
        LilyPond__cygwin.do_configure (self)

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
        for i in glob.glob (('%(install_root)s/usr/bin/*'
                  % self.get_substitution_dict ())):
            s = self.read_pipe ('file %(i)s' % locals ())
            if s.find ('guile') >= 0:
                self.system ('mv %(i)s %(i)s.scm', locals ())
            elif  s.find ('python') >= 0:
                self.system ('mv %(i)s %(i)s.py', locals ())

        for i in self.read_pipe ('''
find %(install_root)s -name "*.ly"
''').split ():
            s = open (i).read ()
            open (i, 'w').write (re.sub ('\r*\n', '\r\n', s))

        self.file_sub ([(r'gs-font-load\s+#f', 'gs-font-load #t')],
        '%(install_root)s/usr/share/lilypond/current/scm/lily.scm')

class LilyPond__debian (LilyPond):
    def __init__ (self, settings):
        LilyPond.__init__ (self, settings)
        self.with (version=settings.lilypond_branch, mirror=cvs.gnu,
             builddeps=['libfontconfig1-dev', 'guile-1.6-dev', 'libpango1.0-dev', 'python-dev'],
             track_development=True)
    def install (self):
        targetpackage.Target_package.install (self)

class LilyPond__darwin (LilyPond):
    def __init__ (self, settings):
        LilyPond.__init__ (self, settings)
        self.with (version=settings.lilypond_branch, mirror=cvs.gnu, track_development=True,
             depends=['pango', 'guile', 'gettext', 'ghostscript', 'fondu', 'osx-lilypad']
             ),

    def configure_command (self):
        cmd = LilyPond.configure_command (self)

        pydir = ('%(system_root)s/System/Library/Frameworks/Python.framework/Versions/%(python_version)s'
            + '/include/python%(python_version)s')

        cmd += ' --with-python-include=' + pydir
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
