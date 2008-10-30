from gub import target

class E2fsprogs (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/e2fsprogs/e2fsprogs-1.38.tar.gz'
    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + ' install-libs')
