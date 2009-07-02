from gub import target

class Libfftw (target.AutoBuild):
    source = 'http://www.fftw.org/fftw-3.2.1.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config',
                ]

