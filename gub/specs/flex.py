from gub import target
from gub import tools

class Flex (target.AutoBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/flex/flex-2.5.35.tar.gz'
    def patch (self):
        target.AutoBuild.patch (self)
        self.file_sub ([('-I@includedir@', '')], '%(srcdir)s/Makefile.in')
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
ac_cv_func_realloc_0_nonnull=yes
'''

class Flex__mingw (Flex):
    dependencies = ['regex']
    configure_variables = Flex.configure_variables + ' LIBS=-lregex'
    def patch (self):
        self.system ('''
mkdir -p %(srcdir)s/sys
cp %(sourcefiledir)s/mingw-headers/wait.h %(srcdir)s/sys
''')

class Flex__tools (tools.AutoBuild):
    source = Flex.source
