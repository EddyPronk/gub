from gub import targetbuild

class E2fsprogs (targetbuild.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/e2fsprogs/e2fsprogs-1.38.tar.gz'
    def install_command (self):
        return (targetbuild.AutoBuild.install_command (self)
                + ' install-libs')
