from gub import targetbuild

class Libpcre (targetbuild.TargetBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/prce/pcre-7.8.tar.bz2'
    def name (self):
        return 'libpcre'
