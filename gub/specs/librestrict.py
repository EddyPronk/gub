from gub import tools

class Librestrict__tools (tools.MakeBuild):
    source = 'url://host/librestrict-1.0.tar.gz'
    def shadow (self):
        self.system ('rm -rf %(builddir)s')
        self.shadow_tree ('%(gubdir)s/librestrict', '%(builddir)s')
    def makeflags (self):
        return 'prefix=%(system_prefix)s'
    def LD_PRELOAD (self):
        return ''

class Librestrict_nomake__tools (Librestrict__tools):
    def compile_command (self):
        return 'gcc -W -Wall -shared -fPIC -o librestrict.so restrict.c'
    def install_command (self):
        return ('mkdir -p %(install_root)s/%(system_prefix)s/lib'
                ' && cp -p librestrict.so %(install_root)s/%(system_prefix)s/lib')

Librestrict__tools = Librestrict_nomake__tools
