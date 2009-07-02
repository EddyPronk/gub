from gub import target

class Jack (target.AutoBuild):
    source = 'svn+http://subversion.jackaudio.org/jack/trunk/jack'
    source = 'http://www.grame.fr/~letz/jack-1.9.2.tar.bz2'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config',]
