from gub import build

class Libqt4_dev (build.BinaryBuild, build.SdkBuild):
    def untar (self):
        build.BinaryBuild.untar (self)
        for i in ('QtCore.pc', 'QtGui.pc', 'QtNetwork.pc'):
            self.file_sub ([('includedir', 'deepqtincludedir')],
                           '%(srcdir)s/usr/lib/pkgconfig/%(i)s',
                           env=locals ())
