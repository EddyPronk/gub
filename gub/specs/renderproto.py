from gub import target

class Renderproto (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/renderproto-0.9.3.tar.gz'
    dependencies = ['tools::libtool']
