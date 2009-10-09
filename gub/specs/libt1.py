from gub import misc
from gub import target
from gub import tools

class Libt1 (target.AutoBuild):
    source = 'ftp://sunsite.unc.edu/pub/Linux/libs/graphics/t1lib-5.1.2.tar.gz'
    parallel_build_broken = True
    srcdir_build_broken = True
    dependencies = [
            'tools::libtool',
            ]
    make_flags = ''' without_doc 'VPATH:=$(srcdir)' '''
    configure_flags = (target.AutoBuild.configure_flags
                       + ' --without-athena'
                       + ' --without-x'
                       + ' --x-includes='
                       + ' --x-libraries='
                       )
    if 'stat' in misc.librestrict ():
        def autoupdate (self):
            target.AutoBuild.autoupdate (self)
            # Cross ...WHAT?
            self.file_sub ([(' (/usr|/opt)', r' %(system_prefix)s\1')],
                           '%(srcdir)s/configure')
        def LD_PRELOAD (self):
            return '%(tools_prefix)s/lib/librestrict-open.so'

class Libt1__tools (tools.AutoBuild, Libt1):
    parallel_build_broken = True
    srcdir_build_broken = True
    dependencies = [
            'libtool',
            ]
