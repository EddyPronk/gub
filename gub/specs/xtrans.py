from gub import target

class Xtrans (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/lib/xtrans-1.2.1.tar.gz'
    dependencies = ['tools::libtool', 'xproto']
