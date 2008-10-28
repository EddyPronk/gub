from gub import targetbuild

class Faad2 (targetbuild.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/faac/faad2-2.5.tar.gz'
    def get_build_dependencies (self):
        return ['tools::autoconf', 'tools::automake', 'tools::libtool']
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p0 < %(patchdir)s/faad2-2.5.patch
mkdir %(srcdir)s/plugins/bmp
''')        

