from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

no_patch = True
class Gzip__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/gzip/gzip-1.3.12.tar.gz'
    patches = ['gzip-1.3.12-glibc-compat.patch']
    if no_patch:
        patches = []
    def patch (self):
        if no_patch:
            for i in ('gzip.c', 'utimens.c', 'utimens.h'):
                self.file_sub ([('(futimens)', r'gz_\1')], '%(srcdir)s/' + i)
        else:
            tools.AutoBuild.patch (self)
