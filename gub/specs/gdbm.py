from gub import tools
import os

class Gdbm__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/gdbm/gdbm-1.8.3.tar.gz'
    patches = ['gdbm-install.patch']
    dependencies = [
            'libtool'
            ]
