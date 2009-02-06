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
    source = 'http://ftp.acc.umu.se/pub/GNOME/sources/gtk+/2.14/gtk+-2.14.7.tar.gz'
    def _get_build_dependencies (self):
        return [x for x in Gtk_x_._get_build_dependencies (self)
                if 'libx' not in x]
    def LDFLAGS (self):
        return '-Wl,-rpath -Wl,%(system_prefix)s/lib %(rpath)s'
    def patch (self):
        self.file_sub ([('gailutil.def', '$(srcdir)/gailutil.def')], '%(srcdir)s/modules/other/gail/libgail-util/Makefile.in', must_succeed=True)
    
''' 2.15.3 does not build for mingw
if /bin/bash ../libtool --mode=compile i686-mingw32-gcc -mwindows -mms-bitfields -DHAVE_CONFIG_H -I. -I/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk -I.. -DG_LOG_DOMAIN=\"Gtk\" -DGTK_LIBDIR=\"/usr/lib\" -DGTK_DATADIR=\"/usr/share\" -DGTK_DATA_PREFIX=\"/usr\" -DGTK_SYSCONFDIR=\"/usr/etc\" -DGTK_VERSION=\"2.15.3\" -DGTK_BINARY_VERSION=\"2.10.0\" -DGTK_HOST=\"i686-pc-mingw32\" -DGTK_COMPILATION -DGTK_PRINT_BACKENDS=\"file,lpr\" -DGTK_PRINT_PREVIEW_COMMAND=\""evince --unlink-tempfile --preview --print-settings %s %f"\" -I.. -I../gtk -I/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3 -I../gdk -I/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gdk -I/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gdk-pixbuf -I../gdk-pixbuf -DGDK_DISABLE_DEPRECATED -DGTK_DISABLE_DEPRECATED -DGTK_FILE_SYSTEM_ENABLE_UNSUPPORTED -DGTK_PRINT_BACKEND_ENABLE_UNSUPPORTED -DG_ENABLE_DEBUG -DG_ERRORCHECK_MUTEXES -mms-bitfields -I/home/janneke/vc/gub/target/mingw/root/usr/include/glib-2.0 -I/home/janneke/vc/gub/target/mingw/root/usr/lib/glib-2.0/include -I/home/janneke/vc/gub/target/mingw/root/usr/include/pango-1.0 -I/home/janneke/vc/gub/target/mingw/root/usr/include/cairo -I/home/janneke/vc/gub/target/mingw/root/usr/include/freetype2 -I/home/janneke/vc/gub/target/mingw/root/usr/include -I/home/janneke/vc/gub/target/mingw/root/usr/include/atk-1.0         -DG_DISABLE_SINGLE_INCLUDES -DATK_DISABLE_SINGLE_INCLUDES -DGDK_PIXBUF_DISABLE_SINGLE_INCLUDES -DGTK_DISABLE_SINGLE_INCLUDES  -DGDK_PIXBUF_DISABLE_DEPRECATED -g -O2 -g -Wall -mms-bitfields -MT gtkstock.lo -MD -MP -MF ".deps/gtkstock.Tpo" \
	  -c -o gtkstock.lo `test -f '/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/gtkstock.c' || echo '/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/'`/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/gtkstock.c; \
	then mv -f ".deps/gtkstock.Tpo" ".deps/gtkstock.Plo"; \
	else rm -f ".deps/gtkstock.Tpo"; exit 1; \
	fi
/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/gtkstatusicon.c: In function 'wndproc':
/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/gtkstatusicon.c:710: error: 'WM_XBUTTONDOWN' undeclared (first use in this function)
/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/gtkstatusicon.c:710: error: (Each undeclared identifier is reported only once
/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/gtkstatusicon.c:710: error: for each function it appears in.)
/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/gtkstatusicon.c:711: error: 'XBUTTON1' undeclared (first use in this function)
/home/janneke/vc/gub/target/mingw/src/gtk+-2.15.3/gtk/gtkstatusicon.c:736: error: 'WM_XBUTTONUP' undeclared (first use in this function)
'''
