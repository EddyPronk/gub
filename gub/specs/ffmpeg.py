from gub import misc
from gub import repository
from gub import targetpackage

class Ffmpeg (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        # FIXME: fixed version for svn, what a mess
        self.revision = '6017'
        repo = repository.Subversion (
            dir=self.get_repodir (),
            source='svn://svn.mplayerhq.hu/ffmpeg',
            branch='trunk',
            module='.',
            revision=self.revision)
        def fixed_version (self):
            return self.revision
        from new import instancemethod
        repo.version = instancemethod (fixed_version, repo, type (repo))
        self.with_vc (repo)
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
        #targetpackage.TargetBuildSpec.configure_command (self)
        return misc.join_lines ('''
CC=%(tool_prefix)sgcc CFLAGS=-fPIC %(srcdir)s/configure
--prefix=%(prefix_dir)s
--cross-prefix=%(cross_prefix)s/bin/%(tool_prefix)s
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
        return (targetpackage.TargetBuildSpec.install_command (self)
                + ' INSTALLSTRIP=')
