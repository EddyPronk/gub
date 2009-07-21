from gub import target

class Libsamplerate (target.AutoBuild):
    source = 'http://www.mega-nerd.com/SRC/libsamplerate-0.1.7.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config',]


class Libsamplerate__darwin__x86 (Libsamplerate):
    def patch (self):
        Libsamplerate.patch (self)
        # somehow retriggers autoconf?!?
#        for i in ('configure.ac', 'configure'):
        for i in ['configure']:
            self.file_sub ([('-fpascal-strings ', ''),], '%(srcdir)s/' + i)
