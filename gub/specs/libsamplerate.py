from gub import target

class Libsamplerate (target.AutoBuild):
    source = 'http://www.mega-nerd.com/SRC/libsamplerate-0.1.7.tar.gz'
    dependencies = ['tools::automake', 'tools::pkg-config',]
