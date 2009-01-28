from gub import build

class Darwin_sdk (build.SdkBuild):
    source = 'http://lilypond.org/download/gub-sources/darwin7-sdk-0.4.tar.gz'
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

        # printf ('FIXME: serialization: this should already be fixed generically by gup:libtool_la_fixup')
        # probably not, this in is SRCDIR! urg.  See if code can be shared
        # with gup.
        import glob
        pat = self.expand ('%(srcdir)s/usr/lib/*.la')
        for a in glob.glob (pat):
            self.file_sub ([(r' (/usr/lib/.*\.la)', r'%(system_root)s\1')], a)

class Darwin_sdk__darwin__x86 (Darwin_sdk):
    source = 'http://lilypond.org/download/gub-sources/darwin8-sdk-0.4.tar.gz'
