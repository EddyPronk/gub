from gub import misc
from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

class Make_make__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/make/make-3.81.tar.gz'
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        self.source._unpack = self.source._unpack_promise_well_behaved
    def patch (self):
        tools.AutoBuild.patch (self)
        self.file_sub ([('"/usr', '"%(system_prefix)s')], '%(srcdir)s/read.c')
        self.file_sub ([('"/usr', '"%(system_prefix)s'),
                        ('"/lib', '"%(system_root)s/lib')], '%(srcdir)s/remake.c')
    def librestrict_name (self):
        return 'librestrict-' + '-'.join (misc.librestrict ())
        #return [self.librestrict_name ()]
    dependencies = ['librestrict']

class Make_build_sh__tools (Make_make__tools):
    compile_command = 'sh build.sh'
    install_command = ('mkdir -p %(install_prefix)s/bin'
                ' && cp -p make %(install_prefix)s/bin')

class Make_build_sh_newmake__tools (Make_make__tools):
    compile_command = ('sh build.sh && PATH=$(pwd):$PATH '
                + Make_make__tools.compile_command)
    install_command = 'PATH=$(pwd):$PATH ' + Make_make__tools.install_command

Make__tools = Make_build_sh_newmake__tools
