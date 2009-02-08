from gub import tools

class Automake__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/automake/automake-1.10.1.tar.gz'
    def _get_build_dependencies (self):
        return ['autoconf']
