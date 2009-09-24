from gub import target

class Libsndfile (target.AutoBuild):
    source = 'http://www.mega-nerd.com/libsndfile/libsndfile-1.0.20.tar.gz'
    dependencies = ['tools::automake', 'tools::pkg-config', 'libtool']
