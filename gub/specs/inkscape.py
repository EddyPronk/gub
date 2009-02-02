from gub import context
from gub import target

class Inkscape (target.AutoBuild):
    source = 'svn:https://inkscape.svn.sourceforge.net/svnroot/inkscape&module=inkscape&branch=trunk&revision=20605'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        target.add_target_dict (self,
                                {'ACLOCAL_FLAGS':
                                     ' -I '.join ([''] + self.aclocal_path ()),
                                 # --as-needed breaks; ugh, this does not clean LDFLAGS
                                 'LD': '',
                                 'LDFLAGS': '',
                                 })
    def patch (self):
        self.file_sub ([('AC_PATH_PROG\(PKG_CONFIG,',
                         'AC_PATH_PROG(ARE_YOU_FREAKING_MAD__OVERRIDING_PKG_CONFIG,')],
                       '%(srcdir)s/configure.ac')
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::gettext', 'tools::intltool', 'tools::pkg-config',
                'boost-devel', 'glibmm-devel', 'gtkmm-devel', 'gtk+-devel', 'gsl-devel', 'popt-devel',
#WARNING: aclocal's directory is /home/janneke/vc/gub/target/tools/root/usr/share/aclocal, but...
#         no file /home/janneke/vc/gub/target/tools/root/usr/share/aclocal/glib-gettext.m4
#         You may see fatal macro warnings below.
#         If these files are installed in /some/dir, set the ACLOCAL_FLAGS 
#         environment variable to "-I /some/dir", or install
#         /home/janneke/vc/gub/target/tools/root/usr/share/aclocal/glib-gettext.m                'tools::glib-devel',
#WARNING: aclocal's directory is /home/janneke/vc/gub/target/tools/root/usr/share/aclocal, but...
#         no file /home/janneke/vc/gub/target/tools/root/usr/share/aclocal/gtk-2.0.m4
#         You may see fatal macro warnings below.
#         If these files are installed in /some/dir, set the ACLOCAL_FLAGS 
#         environment variable to "-I /some/dir", or install
#         /home/janneke/vc/gub/target/tools/root/usr/share/aclocal/gtk-2.0.m4.
#                'tools::gtk+-devel'
                'libgc-devel', 'libpng-devel', 'libsig++-devel', 'libxml2-devel', 'libxslt-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': [x.replace ('-devel', '') for x in self._get_build_dependencies () if 'tools::' not in x and 'cross/' not in x]}
    def aclocal_path (self):
        return ['%(system_prefix)s/share/aclocal']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --disable-lcms'
                + ' --disable-poppler-cairo'
                + ' LDFLAGS= '
                )

