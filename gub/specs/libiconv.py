from gub import target

class Libiconv (target.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.11.tar.gz'
    def force_sequential_build (self):
        return True
    def _get_build_dependencies (self):
        return ['gettext-devel', 'libtool']
    def patch (self):
        target.AutoBuild.patch (self)
        #self.file_sub ([('	  [*][)]', '	  foobar)')],
        #               '%(srcdir)s/src/Makefile.in')
        self.file_sub ([('$(DESTDIR)$(libdir)/libiconv.la', '../lib/libiconv.la')], '%(srcdir)s/src/Makefile.in', use_re=False)
    def install (self):
        target.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s/lib/charset.alias')
