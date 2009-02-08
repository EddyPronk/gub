from gub import build
from gub import misc

class Python_config (build.SdkBuild):
    source = 'url://host/python-config-2.4.1.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::python']
    def install (self):
        build.SdkBuild.install (self)
        misc.dump_python_config (self)

class Python_config__cygwin (Python_config):
    source = 'url://host/python-config-2.5.tar.gz'
