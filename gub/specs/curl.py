from gub import context
from gub import targetbuild
from gub import toolsbuild

class Curl (targetbuild.TargetBuild):
    source = 'http://curl.haxx.se/download/curl-7.19.0.tar.gz'
    def install (self):
        targetbuild.TargetBuild.install (self)
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        self.system ('cp %(install_prefix)s/bin/curl-config %(install_prefix)s%(cross_dir)s/bin/curl-config')
        self.file_sub ([('%(system_prefix)s', '%(prefix_dir)s')]
                       , '%(install_prefix)s/bin/curl-config')
    @context.subst_method
    def config_script (self):
        return 'curl-config'

class Curl__tools (toolsbuild.ToolsBuild):
    source = Curl.source
