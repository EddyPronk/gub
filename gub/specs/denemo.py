from gub import target

class Denemo (target.AutoBuild):
    source = 'git://git.savannah.gnu.org/denemo.git'
    source = 'http://download.savannah.gnu.org/releases/denemo/denemo-0.8.6.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::gettext', 'tools::intltool', 'tools::pkg-config',
                'guile-devel',
                'gtk+-devel',
                'jack-devel',
                'lash-devel',
                'libaubio-devel',
                'libxml2-devel',
                'lilypond',
                'portaudio-devel',
                ]
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': [x.replace ('-devel', '')
                     for x in self._get_build_dependencies ()
                     if 'tools::' not in x and 'cross/' not in x]
                + ['cross/gcc-c++-runtime']
                }
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --with-jack')

class Denemo__mingw (Denemo):
    patches = ['denemo-mingw.patch']
    def _get_build_dependencies (self):
        return [x for x in Denemo._get_build_dependencies (self)
                if x.replace ('-devel', '') not in [
                'jack',
                'lash',
                'lilypond'
                ]]
