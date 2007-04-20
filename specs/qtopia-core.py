import misc
import targetpackage

trolltech = 'ftp://ftp.trolltech.com/qt/source/%(name)s-opensource-src-%(ball_version)s.tar.%(format)s'

class Qtopia_core (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=trolltech, version='4.2.0')

    def configure_command (self):
        return misc.join_lines ('''
bash -x %(srcdir)s/configure
-prefix /usr
-bindir /usr/bin
-libdir /usr/lib
-embedded %(cpu)s
-fast
-headerdir /usr/include
-datadir /usr/share
-sysconfdir /etc
-xplatform %(target_architecture)s
-depths 8,24

-confirm-license
-docdir /usr/share/doc/qtopia
-plugindir /usr/share/qtopia/plugins
-translationdir /usr/share/qtopia/translations
-examplesdir /usr/share/doc/qtopia/examples
-demosdir /usr/share/doc/qtopia/demos
-little-endian
''')
#-depths 4,8,16,18,24,32
#-xplatform linux-%(cpu)s-g++
#-embedded %(target_architecture)s

class Qtopia_core__linux_arm_softfloat (Qtopia_core):
    def patch (self):
        self.system ('''
cd %(srcdir)s/mkspecs/qws && cp -R linux-arm-g++ %(target_architecture)s
''')
        self.file_sub ([('arm', '%(target_architecture)s')],
                       '%(srcdir)s/mkspecs/qws/qmake.conf')

class Qtopia_core__linux__64 (Qtopia_core):
    def patch (self):
        # ugh, dupe
        self.system ('''
cd %(srcdir)s/mkspecs/qws && cp -R linux-x86_64-g++ %(target_architecture)s
cd %(srcdir)s/mkspecs && cp -R linux-g++-64 %(target_architecture)s
''')
        self.file_sub ([('x86_64', '%(target_architecture)s')],
                       '%(srcdir)s/mkspecs/qws/%(target_architecture)s/qmake.conf')
