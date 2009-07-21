from gub import target

class Libsndfile (target.AutoBuild):
    source = 'http://www.mega-nerd.com/libsndfile/libsndfile-1.0.20.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config', 'libtool']

class Libsndfile__darwin__x86 (Libsndfile):
    # FIXME: PROMOTEME to build.py/target.py [or for darwin_x86 only?]
    def patch (self):
        Libsndfile.patch (self)
        # somehow retriggers autoconf?!?
#        for i in ('configure.ac', 'configure'):
        for i in ['configure']:
            self.file_sub ([('-fpascal-strings ', ''),
                            ('-I(/Developer/Headers/FlatCarbon)',
                             r'-I%(system_root)s\1'),
                            ], '%(srcdir)s/' + i)
