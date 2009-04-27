from gub import target

class Hunspell (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/hunspell/hunspell-1.2.8.tar.gz'

class Hunspell__mingw (Hunspell):
    def _get_build_dependencies (self):
        return ['libiconv-devel']
    def configure_command (self):
        return (Hunspell.configure_command (self)
                + ' --disable-nls')
    def patch (self):
        Hunspell.patch (self)
        self.file_sub ([('(chmorph_LDADD.*)',
                         r'\1 ../hunspell/libhunspell-1.2.la')],
                       '%(srcdir)s/src/tools/Makefile.am')
        self.file_sub ([('(chmorph_LDADD.*)',
                         r'\1 ../hunspell/libhunspell-1.2.la'),
                        ('(	../parsers/libparsers.a .*@READLINELIB@)',
                         r'\1 ../hunspell/libhunspell-1.2.la -liconv')],
                       '%(srcdir)s/src/tools/Makefile.in')
