from gub import target

class Libiconv (target.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/libiconv/libiconv-1.11.tar.gz'
    parallel_build_broken = True
    dependencies = ['gettext-devel', 'libtool']
    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([('$(DESTDIR)$(libdir)/libiconv.la', '../lib/libiconv.la')], '%(srcdir)s/src/Makefile.in', use_re=False)
    def install (self):
        target.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s/lib/charset.alias')
