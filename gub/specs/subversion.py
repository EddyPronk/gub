from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

class Subversion__tools (tools.AutoBuild):
    source = 'http://subversion.tigris.org/downloads/subversion-1.6.4.tar.gz'
    def _get_build_dependencies (self):
        return [
            'libapr-util-devel',
                ]
