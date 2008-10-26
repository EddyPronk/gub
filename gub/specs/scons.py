from gub import toolsbuild

class Scons__tools (toolsbuild.ToolsBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/scons/scons-0.98.4.tar.gz'
    def configure (self):
        pass
    def compile (self):
        self.system ('mkdir -p %(builddir)s')
    def install_command (self):
        return 'python %(srcdir)s/setup.py install --prefix=%(tools_prefix)s --root=%(install_root)s'
    def license_files (self):
        return ['%(srcdir)s/LICENSE.txt']
