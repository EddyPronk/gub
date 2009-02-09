from gub import target

class Libx11 (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/lib/libX11-1.1.5.tar.gz'
    def _get_build_dependencies (self):
        return ['libtool', 'inputproto-devel', 'kbproto-devel', 'libxcb-devel', 'xextproto-devel', 'xproto-devel', 'xtrans-devel']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --disable-xf86bigfont'
                + ' --disable-malloc0returnsnull')
    def compile (self):
        self.system ('cd %(builddir)s && make -C src/util makekeys CC=gcc CFLAGS= makekeys_CFLAGS= LDFLAGS=')
        target.AutoBuild.compile (self)
