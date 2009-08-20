import os
#
from gub import misc
from gub import tools

class Autoconf__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/autoconf/autoconf-2.63.tar.gz'
    def _get_build_dependencies (self):
        return [
            'm4',
            'perl',
            ]
    def force_sequential_build (self):
        return True
    def makeflags (self):
        return ('PERL5LIB=%(tools_prefix)s/lib/perl5/5.10.0'
        	+ ':%(tools_prefix)s/lib/perl5/5.10.0/%(build_architecture)s'
                + misc.append_path (os.environ.get ('PERL5LIB', '')))
