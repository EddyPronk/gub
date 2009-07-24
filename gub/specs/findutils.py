from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

class Findutils__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/findutils/findutils-4.4.2.tar.gz'
