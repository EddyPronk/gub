from gub import cross
from gub import mirrors

class Binutils (cross.CrossAutoBuild):
    source = mirrors.with_tarball (name='binutils', mirror=mirrors.gnu, version='2.18', format='bz2')
    patches = ['binutils-2.18-makeinfo-version.patch', 'binutils-2.18-werror.patch' ]
    def get_build_dependencies (self):
        return ['tools::texinfo']
    def xconfigure_command (self):
        # --werror is broken
        return (cross.CrossAutoBuild.configure_command (self)
                + misc.join_lines ('''
--disable-werror
'''))
    def install (self):
        cross.CrossAutoBuild.install (self)
        self.system ('rm %(install_prefix)s/cross/lib/libiberty.a')
