from gub import build

class Saxon_java (build.BinaryBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/saxon/saxonb9-1-0-2j.zip'
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        print 'FIXME: serialization:', __file__, ': strip-components'
        source._version = '9.1.0.2j'
    def untar (self):
        build.BinaryBuild.untar (self)
        self.system ('''
cd %(srcdir)s && ln -f saxon9.jar saxon.jar
cd %(srcdir)s && mkdir -p usr/share/doc usr/share/java
cd %(srcdir)s && mv doc usr/share/doc/saxon
cd %(srcdir)s && mv notices usr/share/doc/saxon
cd %(srcdir)s && mv * usr/share/java || :
''')
