from gub import loggedos
from gub import targetbuild

class Libpcre (targetbuild.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/prce/pcre-7.8.tar.bz2'
    def name (self):
        return 'libpcre'

class Libpcre__mingw (Libpcre):
    def configure (self):
        Libpcre.configure (self)
        # c&p from libxslt
        def fix_allow_undefined (logger, file):
            loggedos.file_sub (logger,
                               [
                    # libtool: link: warning: undefined symbols not allowed in i686-pc-mingw32 shared  libraries
                    ('^(allow_undefined_flag=.*)unsupported', '\\1'),
                    # libtool: install: error: cannot install `libexslt.la' to a directory not ending in /home/janneke/vc/gub/target/mingw/build/libxslt-1.1.24/libexslt/.libs
                    (r'if test "\$inst_prefix_dir" = "\$destdir";', 'if false;'),],
                               file)
        self.map_locate (fix_allow_undefined, '%(builddir)s', 'libtool')
