from gub import context
from gub import loggedos
from gub import misc
from gub import targetbuild

class Libxslt (targetbuild.TargetBuild):
    source = 'http://xmlsoft.org/sources/libxslt-1.1.24.tar.gz'
    def patch (self):
        self.system ('rm -f %(srcdir)s/libxslt/xsltconfig.h')
    def get_build_dependencies (self):
        return ['libxml2-devel', 'zlib-devel']
    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                + misc.join_lines ('''
--without-python
--without-crypto
'''))
    @context.subst_method
    def config_script (self):
        return 'xslt-config'

class Libxslt__mingw (Libxslt):
    def autoconf (self):
        #update libtool so that it will install a dll
        self.runner._execute (commands.ForcedAutogenMagic (self))
    def xxconfigure (self):
        Libxslt.configure (self)
        def libtool_fix_allow_undefined (logger, file):
            loggedos.file_sub (logger,
                               [
                    # libtool: link: warning: undefined symbols not allowed in i686-pc-mingw32 shared  libraries
                    ('^(allow_undefined_flag=.*)unsupported', '\\1'),
                    # libtool: install: error: cannot install `libexslt.la' to a directory not ending in /home/janneke/vc/gub/target/mingw/build/libxslt-1.1.24/libexslt/.libs
                    (r'if test "\$inst_prefix_dir" = "\$destdir";', 'if false;'),],
                               file)
        self.map_locate (fix_allow_undefined, '%(builddir)s', 'libtool')
    def configure_command (self):
        return (Libxslt.configure_command (self)
                + misc.join_lines ('''
--without-plugins
'''))
