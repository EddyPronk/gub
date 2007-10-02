from gub import toolsbuild
from gub import sources
from gub import mirrors

class Flex (toolsbuild.ToolsBuild):
    source = sources.join (sources.sf, 'flex/flex-2.5.4a.tar.gz')
    auto_source = mirrors.with_template (name='flex', version="2.5.4a",
                   mirror=mirrors.sf, format='gz'),
    def srcdir (self):
        return '%(allsrcdir)s/flex-2.5.4'
    def install_command (self):
        return self.broken_install_command ()
    def packaging_suffix_dir (self):
        return ''
    def apply_patch (self):
        self.system ('flex-2.5.4a-FC4.patch')
