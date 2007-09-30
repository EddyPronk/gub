from gub import targetpackage

faac = 'http://surfnet.dl.sourceforge.net/sourceforge/faac/%(name)s-%(ball_version)s.tar.%(format)s'

class Faad2 (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=faac, version='2.5')
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p0 < %(patchdir)s/faad2-2.5.patch
mkdir %(srcdir)s/plugins/bmp
''')        
        self.autoupdate ()

