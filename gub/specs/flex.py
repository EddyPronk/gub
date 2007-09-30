from gub import toolsbuild

class Flex (toolsbuild.ToolsBuild):
    def srcdir (self):
        return '%(allsrcdir)s/flex-2.5.4'
    def install_command (self):
        return self.broken_install_command ()
    def packaging_suffix_dir (self):
        return ''
    def apply_patch (self):
        self.system ('flex-2.5.4a-FC4.patch')
