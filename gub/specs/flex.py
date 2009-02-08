from gub import tools

class Flex__tools (tools.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/flex/flex-2.5.33.tar.gz'

class Flex_old__tools (tools.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/flex/flex-2.5.4a.tar.gz'
    patches = ['flex-2.5.4a-FC4.patch']
    def _get_build_dependencies (self):
        return ['bison']
    def install_command (self):
        return self.broken_install_command (self)
