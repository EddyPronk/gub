from gub import target

class Jack (target.WafBuild):
    source = 'svn+http://subversion.jackaudio.org/jack/trunk/jack'
    source = 'http://www.grame.fr/~letz/jack-1.9.2.tar.bz2'
    dependencies = ['tools::automake', 'tools::pkg-config',]
