from gub import tools

class Make_make__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/make/make-3.81.tar.gz'
    def get_build_dependencies (self):
        return ['librestrict']
    def wrap_executables (self):
        return

class Make_build_sh__tools (Make_make__tools):
    def compile_command (self):
        return 'sh build.sh'
    def install_command (self):
        return ('mkdir -p %(install_root)s/%(system_prefix)s/bin'
                ' && cp -p make %(install_root)s/%(system_prefix)s/bin')

class Make_build_sh_newmake__tools (Make_make__tools):
    def compile_command (self):
        return ('sh build.sh && PATH=:$PATH '
                + Make_make__tools.compile_command (self))
    def install_command (self):
        return 'PATH=:$PATH ' + Make_make__tools.install_command (self)

Make__tools = Make_build_sh_newmake__tools
