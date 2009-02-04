from gub import context
from gub import target

class Gtk_x_ (target.AutoBuild):
    # crashes inkscape
    #    source = 'http://ftp.gnome.org/pub/GNOME/sources/gtk+/2.15/gtk+-2.15.2.tar.gz'
    source = 'http://ftp.gnome.org/pub/GNOME/sources/gtk+/2.15/gtk+-2.15.0.tar.gz'
# Requested 'glib-2.0 >= 2.17.6' but version of GLib is 2.16.1
# FIXME: should bump GNOME deps
#    source = 'http://ftp.acc.umu.se/pub/GNOME/sources/gtk+/2.14/gtk+-2.14.7.tar.gz'
    def get_build_dependencies (self):
        return ['libtool', 'atk-devel', 'cairo-devel', 'libjpeg-devel', 'libpng-devel', 'libtiff-devel',
                #'pango-devel',
                'pangocairo-devel',
                'libxext-devel',
                #, 'libxinerama-devel',
                'libxfixes-devel',
                ]
    @context.subst_method
    def LDFLAGS (self):
#        return '-ldl ' + self.get_substitution_dict ()['LDFLAGS']
#        return '-ldl -Wl,--as-needed %(rpath)s'
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
        #FIXME: add to update_libtool ()
        def libtool_disable_rpath (logger, libtool, file):
            from gub import loggedos
            # Must also keep -rpath $libdir, because when
            # build_arch==target_arch we may run build-time
            # executables.  Either that, or set LD_LIBRARY_PATH
            # somewhere.
            loggedos.file_sub (logger, [('^(hardcode_libdir_flag_spec)=.*',
                                         (r'hardcode_libdir_flag_spec="-Wl,-rpath -Wl,\$libdir'
                                          + self.expand (' %(rpath)s"').replace ('\\$$', "'$'")))],
                               file)
        self.map_locate (lambda logger, file: libtool_disable_rpath (logger, self.expand ('%(system_prefix)s/bin/libtool'), file), '%(builddir)s', 'libtool')

class Gtk_x___mingw (Gtk_x_):
    source = Gtk_x_.source
    def get_build_dependencies (self):
        return [x for x in Gtk_x_.get_build_dependencies (self)
                if 'libx' not in x]
