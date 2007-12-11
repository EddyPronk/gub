from gub import toolsbuild
from gub import misc
from gub import mirrors

class Scons (toolsbuild.ToolsBuild):
    source = mirrors.with_template (name='scons', version='0.96.93',
                   format='gz',
                   mirror=mirrors.sf)
    def stages (self):
        return [s for s in toolsbuild.ToolsBuild.stages (self)
                if s != 'compile']
    def patch (self):
        # FIXME: no autotools
        pass
    def configure (self):
        self.system ('mkdir -p %(builddir)s')
    def install_command (self):
        return 'python %(srcdir)s/setup.py install --prefix=%(tools_prefix)s --root=%(install_root)s'
    def license_files (self):
        return ['%(srcdir)s/LICENSE.txt']
