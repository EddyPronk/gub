from gub import target

class Libsamplerate (target.AutoBuild):
    source = 'http://www.mega-nerd.com/SRC/libsamplerate-0.1.7.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config',]

class Libsamplerate__darwin__x86 (Libsamplerate):
    # FIXME: PROMOTEME to build.py/target.py [or for darwin_x86 only?]
    def patch (self):
        Libsamplerate.patch (self)
        # somehow retriggers autoconf?!?
#        for i in ('configure.ac', 'configure'):
        for i in ['configure']:
            self.file_sub ([('-fpascal-strings ', ''),
                            ('-I(/Developer/Headers/FlatCarbon)',
                             r'-I%(system_root)s\1'),
                            ], '%(srcdir)s/' + i)
