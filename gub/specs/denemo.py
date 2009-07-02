from gub import misc
from gub import repository
from gub import target

class Denemo (target.AutoBuild):
    source = 'git://git.savannah.gnu.org/denemo.git'
    source = 'http://download.savannah.gnu.org/releases/denemo/denemo-0.8.6.tar.gz'
    @staticmethod
    def version_from_VERSION (self):
        try:
            s = self.read_file ('VERSION')
            if 'MAJOR_VERSION' in s:
                d = misc.grok_sh_variables_str (s)
                return '%(MAJOR_VERSION)s.%(MINOR_VERSION)s.%(PATCH_LEVEL)s' % d
        except:
            pass
        return '8.6.0'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        if isinstance (source, repository.Git):
            source.version = misc.bind_method (Denemo.version_from_VERSION, source)
        else:
            return
            def tracking (self):
                return True
            # let's keep srdir around for now
            self.source.is_tracking = misc.bind_method (tracking, self.source)
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::gettext', 'tools::intltool', 'tools::pkg-config',
                'guile-devel',
                'gtk+-devel',
                'jack-devel',
                'lash-devel',
                'libaubio-devel',
                'libxml2-devel',
                'lilypondcairo',
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
                + ' --with-jack'
                + ' --program-prefix=')

class Denemo__mingw (Denemo):
    patches = ['denemo-mingw.patch', 'denemo-relocate-mingw.patch']
    def _get_build_dependencies (self):
        return [x for x in Denemo._get_build_dependencies (self)
                if x.replace ('-devel', '') not in [
                'jack',
                'lash',
                'lilypondcairo',
                ]]
