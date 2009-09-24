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
    def force_autoupdate (self):
        return True
    # FIXME: libaubio blindly includes /usr/include, /usr/include/python2.4, ..
    def XXpatch (self):
        target.AutoBuild.patch (self)
        for i in ['%(srcdir)s/python/aubio/Makefile.am',
                  '%(srcdir)s/python/aubio/Makefile.in']:
            self.file_sub ([('-I(\$\{prefix\}|/usr)/include(/python(\$\{PYTHON_VERSION\}|[0-9.]+))?', ''),],
                       i)
    def XXconfigure_command (self):
        return (target.AutoBuild.configure_command (self)
                + 'CPPFLAGS="-I%(system_prefix)s/include `python-config --cflags`"'
                + 'LDFLAGS="`python-config --ldflags`"')
    # ... no configure options, just cache it out
    def config_cache_overrides (self, string):
        return (string + '''
ac_cv_path_PYTHON=${ac_cv_path_PYTHON=no}
ac_cv_path_SWIG=${ac_cv_path_SWIG=no}
''')
