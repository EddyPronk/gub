from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

class Subversion__tools (tools.AutoBuild):
    source = 'http://subversion.tigris.org/downloads/subversion-1.6.4.tar.gz'
    dependencies = [
            'libapr-util-devel',
            'sqlite',
            'libxml2'
            ]
