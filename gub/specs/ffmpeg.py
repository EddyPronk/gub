from gub import misc
from gub import target

class Ffmpeg (target.AutoBuild):
    source='svn://svn.mplayerhq.hu/ffmpeg&branch=trunk&revision=6017'
    def version (self):
        return self.revision
    def _get_build_dependencies (self):
        return ['faac-devel', 'faad2-devel', 'a52dec-devel']
    def configure_command (self):
        #FIXME: this is autoconf
        #target.AutoBuild.configure_command (self)
        return misc.join_lines ('''
CC=%(toolchain_prefix)sgcc CFLAGS=-fPIC %(srcdir)s/configure
--prefix=%(prefix_dir)s
--cross-prefix=%(cross_prefix)s/bin/%(toolchain_prefix)s
--cpu=%(cpu)s
--enable-faad
--enable-a52
--enable-a52bin
--enable-pp
--enable-shared
--enable-pthreads
--enable-gpl
--disable-audio-beos
--disable-v4l
--disable-dv1394
--disable-ffserver
--disable-ffplay
--disable-debug
--disable-opts
''')
    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + ' INSTALLSTRIP=')
