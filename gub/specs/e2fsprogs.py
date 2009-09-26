from gub import target

# FIXME: updateme and dependants, package has finally been split
# http://sourceforge.net/projects/e2fsprogs/files/
class E2fsprogs (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/e2fsprogs/e2fsprogs-1.38.tar.gz'
    configure_flags = (target.AutoBuild.configure_flags
                       + '  --enable-elf-shlibs')
    install_command = (target.AutoBuild.install_command
                + ' install-libs')
