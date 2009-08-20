from gub import tools
import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

class Gzip__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/gzip/gzip-1.3.12.tar.gz'
    patches = ['gzip-1.3.12-glibc-compat.patch']
