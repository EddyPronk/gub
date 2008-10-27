from gub import mirrors
from gub import targetbuild

faac = 'http://surfnet.dl.sourceforge.net/sourceforge/faac/%(name)s-%(ball_version)s.tar.%(format)s'

class Faad2 (targetbuild.AutoBuild):
    source = mirrors.with_tarball (name='faad2', mirror=faac, version='2.5')
    def get_build_dependencies (self):
        return ['tools::autoconf', 'tools::automake', 'tools::libtool']
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p0 < %(patchdir)s/faad2-2.5.patch
mkdir %(srcdir)s/plugins/bmp
''')        

