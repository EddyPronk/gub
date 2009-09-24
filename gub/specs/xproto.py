from gub import target

class Xproto (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/proto/xproto-7.0.13.tar.gz'
    dependencies = ['tools::libtool']
