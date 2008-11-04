from gub import tools

class Make__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/make/make-3.81.tar.gz'
    def get_build_dependencies (self):
        return ['librestrict']
    def wrap_executables (self):
        return
