from gub import gubb

class Libqt4_dev (gubb.BinarySpec, gubb.SdkBuildSpec):
    def untar (self):
        gubb.BinarySpec.untar (self)
        for i in ('QtCore.pc', 'QtGui.pc', 'QtNetwork.pc'):
            self.file_sub ([('includedir', 'deepqtincludedir')],
                           '%(srcdir)s/usr/lib/pkgconfig/%(i)s',
                           env=locals ())
