from gub import context
from gub import target

class Gtk_x_ (target.AutoBuild):
    # crashes inkscape
    #    source = 'http://ftp.gnome.org/pub/GNOME/sources/gtk+/2.15/gtk+-2.15.2.tar.gz'
    #source = 'http://ftp.gnome.org/pub/GNOME/sources/gtk+/2.15/gtk+-2.15.0.tar.gz'
    source = 'http://ftp.gnome.org/pub/GNOME/sources/gtk+/2.15/gtk+-2.15.3.tar.gz'
# Requested 'glib-2.0 >= 2.17.6' but version of GLib is 2.16.1
# FIXME: should bump GNOME deps
#    source = 'http://ftp.acc.umu.se/pub/GNOME/sources/gtk+/2.14/gtk+-2.14.7.tar.gz'
    def _get_build_dependencies (self):
        return ['libtool', 'atk-devel', 'cairo-devel', 'libjpeg-devel', 'libpng-devel', 'libtiff-devel',
                #'pango-devel',
                'pangocairo-devel',
                'libxext-devel',
                #, 'libxinerama-devel',
                'libxfixes-devel',
                ]
    @context.subst_method
    def LDFLAGS (self):
#        return '-ldl -Wl,--as-needed'
        # UGH. glib-2.0.m4's configure snippet compiles and runs a
        # program linked against glib; so it needs LD_LIBRARY_PATH (or
        # a configure-time-only -Wl,-rpath, -Wl,%(system_prefix)s/lib
#        return '-ldl -Wl,--as-needed %(rpath)s'
        return '-ldl -Wl,--as-needed -Wl,-rpath -Wl,%(system_prefix)s/lib %(rpath)s'
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ''' LDFLAGS='%(LDFLAGS)s' '''
                + ' --without-libjasper'
                + ' --disable-cups')

class Gtk_x___mingw (Gtk_x_):
    source = Gtk_x_.source
    def get_build_dependencies (self):
        return [x for x in Gtk_x_.get_build_dependencies (self)
                if 'libx' not in x]
