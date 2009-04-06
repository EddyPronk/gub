from gub import build
from gub import misc

class Pytt (build.NullBuild):
    source = 'url://host/pytt-1.0.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::python']
    def install (self):
        build.NullBuild.install (self)
        misc.dump_python_script (self, '%(install_prefix)s/bin', 'pytt')
