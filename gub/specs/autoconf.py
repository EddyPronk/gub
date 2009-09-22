import os
#
from gub import misc
from gub import tools

class Autoconf__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/autoconf/autoconf-2.63.tar.gz'
    parallel_build_broken = True
    def _get_build_dependencies (self):
        return [
            'm4',
            'perl',
            ]
