from gub import tools

class Flex__tools (tools.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/flex/flex-2.5.33.tar.gz'
    def get_build_dependencies (self):
        return ['bison']
    def install_command (self):
        return self.broken_install_command ()
    def packaging_suffix_dir (self):
        return ''
    def apply_patch (self):
        self.system ('flex-2.5.4a-FC4.patch')
