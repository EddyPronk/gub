from gub import cross

class Binutils (cross.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/binutils/binutils-2.18.tar.bz2'
    patches = ['binutils-2.18-makeinfo-version.patch', 'binutils-2.18-werror.patch' ]
    def get_build_dependencies (self):
        return ['tools::texinfo']
    def xconfigure_command (self):
        # --werror is broken
        return (cross.AutoBuild.configure_command (self)
                + misc.join_lines ('''
--disable-werror
'''))
    def install (self):
        cross.AutoBuild.install (self)
        self.system ('rm %(install_prefix)s/cross/lib/libiberty.a')

class Binutils__linux__ppc (Binutils):
    source = Binutils.source
    patches = Binutils.patches + ['binutils-2.18-werror-ppc.patch']
