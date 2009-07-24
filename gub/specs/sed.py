from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

class Sed__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/sed/sed-4.1.5.tar.gz'
