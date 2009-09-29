from gub import target
from gub import tools

class Wget (target.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/wget/wget-1.11.4.tar.gz'

class Wget__mingw (Wget):
    patches = ['wget-1.11.4-mingw.patch']
    
class Wget__tools (tools.AutoBuild, Wget):
    pass
