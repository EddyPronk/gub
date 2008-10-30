from gub import context
from gub import misc
from gub import target

# TODO: base class Qmake build.
#       sort-out what exactly is Qmake build, qt, and qtopia-core specific

class Qtopia_core (target.AutoBuild):
    source = 'ftp://ftp.trolltech.com/qt/source/qtopia-core-opensource-src-4.2.2.tar.gz'
        dict = {
            'CC': 'gcc',
            'CXX': 'g++',
            #'LINK': '%(toolchain_prefix)sg++',
            }
        build.change_target_dict (self, dict)
    def _get_build_dependencies (self):
        return ['freetype', 'tslib']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': self._get_build_dependencies ()}
    def patch (self):
        self.file_sub ([('pkg-config', '$PKG_CONFIG')],
                       '%(srcdir)s/configure')
    def configure_command (self):
#unset CC CXX; bash -x %(srcdir)s/configure
        return misc.join_lines ('''
unset CC CXX; bash %(srcdir)s/configure
-prefix %(prefix_dir)s
-bindir %(prefix_dir)s/bin
-libdir %(prefix_dir)s/lib
-embedded %(cpu)s
-fast
-headerdir %(prefix_dir)s/include
-datadir %(prefix_dir)s/share
-sysconfdir /etc
-xplatform qws/%(qmake_target_architecture)s
-depths 8,16,32

-little-endian
-release
-no-cups
-no-accessibility
-no-freetype
-no-glib
-nomake demos
-nomake examples
-nomake tools
-qt-mouse-tslib
-qt-libjpeg

-confirm-license

-docdir %(prefix_dir)s/share/doc/qtopia
-plugindir %(prefix_dir)s/share/qtopia/plugins
-translationdir %(prefix_dir)s/share/qtopia/translations
-examplesdir %(prefix_dir)s/share/doc/qtopia/examples
-demosdir %(prefix_dir)s/share/doc/qtopia/demos
-verbose
''')
    def configure (self):
        target.AutoBuild.configure (self)
        def dosub (logger, fname):
            loggedos.file_sub (logger,
                               [('-I/usr', self.expand ('-I%(system_prefix)s'))],
                               fname)
        self.map_locate (dosub, self.expand ('%(install_root)s'), 'Makefile')
    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + ' INSTALL_ROOT=%(install_root)s')
    def license_files (self):
        return ['%(srcdir)s/LICENSE.GPL']
    def install (self):
        target.AutoBuild.install (self)
        self.system ('mkdir -p %(install_prefix)s/lib/pkgconfig')
        for i in ('QtCore.pc', 'QtGui.pc', 'QtNetwork.pc'):
            self.system ('''
mv %(install_prefix)s/lib/%(i)s %(install_prefix)s/lib/pkgconfig/%(i)s
''',
                         locals ())
            self.file_sub ([('includedir', 'deepqtincludedir')],
                           '%(install_prefix)s/lib/pkgconfig/%(i)s',
                           env=locals ())

class Qtopia_core__linux__arm__softfloat (Qtopia_core):
    @context.subst_method
    def qmake_target_architecture (self):
        return 'linux-arm-g++'
    def patch (self):
        Qtopia_core.patch (self)
        self.file_sub ([('arm-linux', '%(target_architecture)s')],
                       '%(srcdir)s/mkspecs/qws/%(qmake_target_architecture)s/qmake.conf')

Qtopia_core__linux__arm__vfp = Qtopia_core__linux__arm__softfloat

class Qtopia_core__linux__x86 (Qtopia_core):
    @context.subst_method
    def qmake_target_architecture (self):
        return 'linux-x86-g++'
    def patch (self):
        Qtopia_core.patch (self)
        # ugh, dupe
        self.system ('''
cd %(srcdir)s/mkspecs && cp -R linux-g++ %(qmake_target_architecture)s
''')
        self.file_sub ([
                ('= gcc', '= %(target_architecture)s-gcc'),
                ('= g\+\+', '= %(target_architecture)s-g++'),
                ('= ar', '= %(target_architecture)s-ar'),
                ('= ranlib', '= %(target_architecture)s-ranlib'),
                ],
                       '%(srcdir)s/mkspecs/qws/%(qmake_target_architecture)s/qmake.conf')

class Qtopia_core__linux__64 (Qtopia_core__linux__x86):
    @context.subst_method
    def qmake_target_architecture (self):
        return 'linux-x86_64-g++'
