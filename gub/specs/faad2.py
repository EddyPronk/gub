from gub import targetbuild

faac = 'http://surfnet.dl.sourceforge.net/sourceforge/faac/%(name)s-%(ball_version)s.tar.%(format)s'

class Faad2 (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_tarball (mirror=faac, version='2.5')
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p0 < %(patchdir)s/faad2-2.5.patch
mkdir %(srcdir)s/plugins/bmp
''')        
        self.autoupdate ()

