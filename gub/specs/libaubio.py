from gub import target

#Currently, aubio depends on libsndfile, libsamplerate and FFTW. On
#Linux platforms, aubio can be built using JACK, and ALSA.

class Libaubio (target.AutoBuild):
    source = 'http://aubio.org/pub/aubio-0.3.2.tar.gz'
    patches = ['libaubio-pkg-config-override.patch']
    dependencies = ['tools::automake', 'tools::pkg-config',
                'libfftw-devel',
                'libsamplerate-devel',
                'libsndfile-devel',
                'python-devel',
                ]
    force_autoupdate = True
    config_cache_overrides = (target.AutoBuild.config_cache_overrides + '''
ac_cv_path_PYTHON=${ac_cv_path_PYTHON=no}
ac_cv_path_SWIG=${ac_cv_path_SWIG=no}
''')
