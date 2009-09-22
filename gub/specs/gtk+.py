from gub import context
from gub import target

class Gtk_x_ (target.AutoBuild):
    #source = 'http://ftp.gnome.org/pub/GNOME/sources/gtk+/2.15/gtk+-2.15.3.tar.gz'
    source = gnome.platform ('gtk+')
    patches = ['gtk+-2.15.3-substitute-env.patch']
    def _get_build_dependencies (self):
        return ['libtool',
                'atk-devel',
                'cairo-devel',
                'libjpeg-devel',
                'libpng-devel',
                'libtiff-devel',
                #'pango-devel',
                'pangocairo-devel',
                'libxext-devel',
                #, 'libxinerama-devel',
                'libxfixes-devel',
                ]
    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([
                (' demos ', ' '), # actually, we'd need tools::gtk+
                (' tests ', ' '),
                ], '%(srcdir)s/Makefile.in')
    def configure_command (self):
        return (' export gio_can_sniff=yes; '
                + target.AutoBuild.configure_command (self)
                + ' --without-libjasper'
                + ' --disable-cups')
    def create_config_files (self, prefix='/usr'):
        gtk_module_version = '2.10.0' #FIXME!
        etc = self.expand ('%(install_root)s/%(prefix)s/etc/gtk-2.0', locals ())
        self.dump ('''
setdir GTK_PREFIX=$INSTALLER_PREFIX
set GTK_MODULE_VERSION=%(gtk_module_version)s
set GTK_SO_EXTENSION=%(so_extension)s
''', '%(install_prefix)s/etc/relocate/gtk+.reloc', env=locals ())
        self.copy ('%(sourcefiledir)s/gdk-pixbuf.loaders', etc)
    def install (self):
        target.AutoBuild.install (self)
        self.create_config_files ()

class Gtk_x___freebsd (Gtk_x_):
    def configure_command (self):
        return (Gtk_x_.configure_command (self)
                + ' CFLAGS=-pthread')

class Gtk_x___freebsd__x86 (Gtk_x___freebsd):
    patches = Gtk_x___freebsd.patches + ['gtk+-2.15.3-configure.in-have-iswalnum.patch']

class Gtk_x_without_X11 (Gtk_x_):
    def _get_build_dependencies (self):
        return [x for x in Gtk_x_._get_build_dependencies (self)
                if 'libx' not in x]

class Gtk_x___mingw (Gtk_x_without_X11):
    def patch (self):
        Gtk_x_.patch (self)

class Gtk_x___darwin (Gtk_x_without_X11):
    def configure_command (self):
        return (Gtk_x_without_X11.configure_command (self)
                + ' --with-gdktarget=quartz'
                )
