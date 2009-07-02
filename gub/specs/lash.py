from gub import target

class Lash (target.AutoBuild):
    source = 'http://www.very-clever.com/download/nongnu/lash/lash-0.6.0%7Erc2.tar.bz2'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config',]
