from gub import target

class Glibmm (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.18/glibmm-2.18.1.tar.gz'
    def _get_build_dependencies (self):
        return ['glib-devel', 'libsig++-devel']

class Glibmm__freebsd__x86 (Glibmm):
    #source = 'http://ftp.gnome.org/pub/GNOME/sources/glibmm/2.19/glibmm-2.19.2.tar.gz'
    def patch (self):
        Glibmm.patch (self)
        self.file_sub ([('(SUBDIRS = .*) examples( .*)', r'\1\2')],
                         '%(srcdir)s/Makefile.in')
