from gub import context
from gub import gubb
from gub import misc
from gub import targetpackage

trolltech = 'ftp://ftp.trolltech.com/qt/source/%(name)s-opensource-src-%(ball_version)s.tar.%(format)s'

# TODO: base class Qmake build.
#       sort-out what exactly is Qmake build, qt, and qtopia-core specific

class Qtopia_core (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=trolltech, version='4.2.2')
        dict = {
            'CC': 'gcc',
            'CXX': 'g++',
            #'LINK': '%(tool_prefix)sg++',
            }
        gubb.change_target_dict (self, dict)
    def get_build_dependencies (self):
        return ['freetype', 'glib', 'tslib']
    def patch (self):
        self.file_sub ([('pkg-config', '$PKG_CONFIG')],
                       '%(srcdir)s/configure')
    def configure_command (self):
        return misc.join_lines ('''
unset CC CXX; bash -x %(srcdir)s/configure
-prefix /usr
-bindir /usr/bin
-libdir /usr/lib
-embedded %(cpu)s
-fast
-headerdir /usr/include
-datadir /usr/share
-sysconfdir /etc
-xplatform qws/%(qmake_target_architecture)s
-depths 8,24

-little-endian
-release
-no-cups
-no-accessibility
-no-freetype
-nomake demos
-nomake examples
-nomake tools
-qt-mouse-tslib
-qt-libjpeg

-confirm-license

-docdir /usr/share/doc/qtopia
-plugindir /usr/share/qtopia/plugins
-translationdir /usr/share/qtopia/translations
-examplesdir /usr/share/doc/qtopia/examples
-demosdir /usr/share/doc/qtopia/demos
-verbose
''')
    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        for i in misc.find (self.expand ('%(install_root)s'), 'Makefile'):
            self.file_sub ([('-I/usr', '-I%(system_root)/usr')], i)
    def install_command (self):
        return (targetpackage.TargetBuildSpec.install_command (self)
                + ' INSTALL_ROOT=%(install_root)s')
    def license_file (self):
        return '%(srcdir)s/LICENSE.GPL'
    def install (self):
        targetpackage.TargetBuildSpec.install (self)
        self.system ('mkdir -p %(install_root)s/usr/lib/pkgconfig')
        for i in ('QtCore.pc', 'QtGui.pc', 'QtNetwork.pc'):
            self.system ('''
mv %(install_root)s/usr/lib/%(i)s %(install_root)s/usr/lib/pkgconfig/%(i)s
''',
                         locals ())
            self.file_sub ([('includedir', 'deepqtincludedir')],
                           '%(install_root)s/usr/lib/pkgconfig/%(i)s',
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

class Qtopia_core__linux__64 (Qtopia_core):
    @context.subst_method
    def qmake_target_architecture (self):
        return 'linux-x86_64-g++'
    def patch (self):
        Qtopia_core.patch (self)
        # ugh, dupe
        self.system ('''
#cd %(srcdir)s/mkspecs/qws && cp -R linux-x86_64-g++ %(target_architecture)s
cd %(srcdir)s/mkspecs && cp -R linux-g++ %(qmake_target_architecture)s
''')
        self.file_sub ([
                ('= gcc', '= %(target_architecture)s-gcc'),
                ('= g\+\+', '= %(target_architecture)s-g++'),
                ('= ar', '= %(target_architecture)s-ar'),
                ('= ranlib', '= %(target_architecture)s-ranlib'),
                ],
                       '%(srcdir)s/mkspecs/qws/%(target_architecture)s/qmake.conf')
