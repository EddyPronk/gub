from gub import gubb

class Darwin_sdk (gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.SdkBuildSpec.__init__ (self, settings)
        os_version = 7
        if settings.platform == 'darwin-x86':
            os_version = 8
        from gub import repository
        self.with_vc (repository.TarBall (settings.downloads,
                                          url='http://lilypond.org/download/gub-sources/darwin%d-sdk-0.4.tar.gz' % os_version,
                                          version='0.4'))
    def patch (self):
        self.system ('''
rm %(srcdir)s/usr/lib/libgcc*
rm %(srcdir)s/usr/lib/libstdc\+\+*
rm %(srcdir)s/usr/lib/libltdl*
rm %(srcdir)s/usr/include/ltdl.h
rm -f %(srcdir)s/usr/lib/gcc/*-apple-darwin*/*/*dylib
rm -rf %(srcdir)s/usr/lib/gcc
''')

        ## ugh, need to have gcc/3.3/machine/limits.h
        ### self.system ('rm -rf %(srcdir)s/usr/include/gcc')
        ##self.system ('rm -rf %(srcdir)s/usr/include/machine/limits.h')

        ## limits.h symlinks into GCC.

        import glob
        pat = self.expand ('%(srcdir)s/usr/lib/*.la')
        for a in glob.glob (pat):
            self.file_sub ([(r' (/usr/lib/.*\.la)', r'%(system_root)s\1')], a)
