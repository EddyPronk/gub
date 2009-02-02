from gub import context
from gub import target

class Gtk_x_ (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/gtk+/2.15/gtk+-2.15.2.tar.gz'
# Requested 'glib-2.0 >= 2.17.6' but version of GLib is 2.16.1
# FIXME: should bump GNOME deps
#    source = 'http://ftp.acc.umu.se/pub/GNOME/sources/gtk+/2.14/gtk+-2.14.7.tar.gz'
    def get_build_dependencies (self):
        return ['libtool', 'atk-devel', 'cairo-devel', 'libjpeg-devel', 'libpng-devel', 'libtiff-devel',
                #'pango-devel',
                'pangocairo-devel',
                'libxext-devel'] #, 'libxinerama-devel']
    @context.subst_method
    def LDFLAGS (self):
#        return '-ldl ' + self.get_substitution_dict ()['LDFLAGS']
        return '-ldl -Wl,--as-needed'
    def configure_command (self):
        return ('''LDFLAGS='%(LDFLAGS)s' '''
                + target.AutoBuild.configure_command (self)
                + ' --without-libjasper'
                + ' --disable-cups')
    def configure (self):
        target.AutoBuild.configure (self)
        '''
libtool: install: error: cannot install `libgdk-x11-2.0.la' to a directory not ending in /home/janneke/vc/gub/target/linux-64/build/gtk+-2.15.2/gdk/.libs
make[4]: *** [install-libLTLIBRARIES] Error 1
'''
        self.update_libtool ()
    #@context.subst_method
    def urgLD_LIBRARY_PATH (self):
        # UGH. configure runs program linked against libX11; so it
        # needs LD_LIBRARY_PATH or a configure-time-only -Wl,-rpath,
        # -Wl,%(system_prefix)s/lib
###    /home/janneke/vc/gub/target/linux-64/root/usr/lib/libX11.so: undefined reference to `dlsym'
        return '%(system_prefix)s/lib'
