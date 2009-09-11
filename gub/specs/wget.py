from gub import target
from gub import tools

class Wget (target.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/wget/wget-1.11.4.tar.gz'

class Wget__mingw (Wget):
    patches = ['wget-1.11.4-mingw.patch']
    def XXX_need_to_patch_anyway_patch (self):
        Wget.patch (self)
        self.file_sub ([('(xmalloc[.]o)', r'\1 mswindows.o')],
                       '%(srcdir)s/src/Makefile.in')
    def XXX_need_to_patch_anyway_configure_command (self):
        return (Wget.configure_command (self)
                + ' CFLAGS=-DWINDOWS'
                + ' LIBS=-lwsock32')
    
class Wget__tools (tools.AutoBuild, Wget):
    pass
