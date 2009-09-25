from gub import tools

class Flex_old__tools (tools.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/flex/flex-2.5.4a.tar.gz'
    patches = ['flex-2.5.4a-FC4.patch']
    dependencies = ['bison']
    destdir_install_broken = True
