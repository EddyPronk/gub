from gub import target

# FIXME: updateme and dependants, package has finally been split
# http://sourceforge.net/projects/e2fsprogs/files/
class E2fsprogs (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/e2fsprogs/e2fsprogs-1.38.tar.gz'
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + '  --enable-elf-shlibs')
    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + ' install-libs')
