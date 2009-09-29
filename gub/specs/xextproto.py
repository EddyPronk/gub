from gub import target

class Xextproto (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/proto/xextproto-7.0.3.tar.gz'
    dependencies = ['tools::libtool']
