from gub import build
from gub import misc

class Python_config (build.SdkBuild):
    source = 'url://host/python-config-2.4.1.tar.gz'
    dependencies = ['tools::python']
    def install (self):
        build.SdkBuild.install (self)
        misc.dump_python_config (self)
