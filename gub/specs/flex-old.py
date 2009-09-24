from gub import tools

class Flex_old__tools (tools.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/flex/flex-2.5.4a.tar.gz'
    patches = ['flex-2.5.4a-FC4.patch']
    dependencies = ['bison']
    def install_command (self):
        return self.broken_install_command (self)
