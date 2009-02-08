from gub import target

class Faad2 (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/faac/faad2-2.5.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::autoconf', 'tools::automake', 'tools::libtool']
    def patch (self):
        self.system ('''
cd %(srcdir)s && patch -p0 < %(patchdir)s/faad2-2.5.patch
mkdir %(srcdir)s/plugins/bmp
''')        

