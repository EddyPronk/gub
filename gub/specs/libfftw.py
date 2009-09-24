from gub import target

class Libfftw (target.AutoBuild):
    source = 'http://www.fftw.org/fftw-3.2.1.tar.gz'
    dependencies = ['tools::automake', 'tools::libtool', 'tools::pkg-config',]
