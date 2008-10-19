from gub import build

class Libwsock32 (build.BinaryBuild):
#    source = 'http://ftp.debian.org/debian/pool/main/w/wine/wine_0.9.25-2.1_i386.deb'
#    source = 'http://lilypond.org/download/gub-sources/libwsock32-0.9.24-2.1.tar.gz'
    source = 'http://lilypond.org/download/gub-sources/libwsock32-1.0.tar.gz'
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        print 'FIXME: serialization:', __file__, ': version'
#        source._version = '0.9.25-2.1'
        source._version = '1.0'
