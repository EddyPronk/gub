from gub import misc
from gub import targetbuild

class Ffmpeg (targetbuild.AutoBuild):
    source='svn://svn.mplayerhq.hu/ffmpeg&branch=trunk&revision=6017'
    def version (self):
        return self.revision
    def _get_build_dependencies (self):
        return ['faac', 'faad2', 'a52dec']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': self._get_build_dependencies ()}
    def configure_command (self):
        #FIXME: this is autoconf
        #targetbuild.AutoBuild.configure_command (self)
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
        return (targetbuild.AutoBuild.install_command (self)
                + ' INSTALLSTRIP=')
