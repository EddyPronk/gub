from gub import cross
from gub import mirrors

class Binutils (cross.CrossToolsBuild):
    source = mirrors.with_tarball (name='binutils', mirror=mirrors.gnu, version='2.18', format='bz2')
    patches = ['binutils-2.18-makeinfo-version.patch', 'binutils-2.18-werror.patch' ]
    def xconfigure_command (self):
        # --werror is broken
        return (cross.CrossToolsBuild.configure_command (self)
                + misc.join_lines ('''
--disable-werror
'''))
    def install (self):
        cross.CrossToolsBuild.install (self)
        self.system ('rm %(install_prefix)s/cross/lib/libiberty.a')
