from gub import context
from gub import target
from gub import tools

class Curl (target.AutoBuild):
    source = 'http://curl.haxx.se/download/curl-7.19.0.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ''' LDFLAGS='%(rpath)s -Wl,-rpath -Wl,%(system_prefix)s/lib' ''')
    def install (self):
        target.AutoBuild.install (self)
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        self.system ('cp %(install_prefix)s/bin/curl-config %(install_prefix)s%(cross_dir)s/bin/curl-config')
        self.file_sub ([('%(system_prefix)s', '%(prefix_dir)s')]
                       , '%(install_prefix)s/bin/curl-config')
    @context.subst_method
    def config_script (self):
        return 'curl-config'

class Curl__tools (tools.AutoBuild, Curl):
    def _get_build_dependencies (self):
        return ['libtool']
    def configure_command (self):
        return (tools.AutoBuild.configure_command (self)
                + ''' LDFLAGS='-L%(system_prefix)s/lib %(rpath)s -Wl,-rpath -Wl,%(system_prefix)s/lib' ''')
