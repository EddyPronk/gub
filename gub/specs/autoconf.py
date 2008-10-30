from gub import tools

class Autoconf (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/autoconf/autoconf-2.61.tar.gz'
    def force_sequential_build (self):
        return True
