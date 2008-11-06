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
        # URG, must *not* have U __stack_chk_fail@@GLIBC_2.4
        # because glibc-[core-]2.3 will not install with LD_PRELOAD
        command = '-W -Wall -shared -fPIC -o librestrict.so restrict.c'
        return '(gcc -fno-stack-protector %(command)s || gcc %(command)s)' % locals ()
    def install_command (self):
        return ('mkdir -p %(install_root)s/%(system_prefix)s/lib'
                ' && cp -p librestrict.so %(install_root)s/%(system_prefix)s/lib')

Librestrict__tools = Librestrict_nomake__tools
