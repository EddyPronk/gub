from gub import target

class Portaudio (target.AutoBuild):
    source = 'http://www.portaudio.com/archives/pa_stable_v19_20071207.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config',]

class Portaudio__mingw (Portaudio):
    def patch (self):
        Portaudio.patch (self)
        for i in ['%(srcdir)s/configure.in',
                  '%(srcdir)s/configure']:
            self.file_sub ([('((src/os/win)/pa_win_util.o)',
                             r'\1 \2/pa_win_waveformat.o',)],
                           i)
