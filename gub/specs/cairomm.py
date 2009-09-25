from gub import target

class Cairomm (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/cairomm-1.8.0.tar.gz'
    dependencies = ['cairo-devel', 'libsig++-devel']

class Cairomm__freebsd (Cairomm):
    configure_variables = (Cairomm.configure_variables
                           + ' CFLAGS=-pthread CXXFLAGS=-pthread')
