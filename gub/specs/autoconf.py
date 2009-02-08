from gub import tools

class Autoconf__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/autoconf/autoconf-2.63.tar.gz'
    def _get_build_dependencies (self):
        return ['m4']
    def force_sequential_build (self):
        return True
