from gub import context
from gub import target

class Cairomm (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/cairomm-1.8.0.tar.gz'
    def _get_build_dependencies (self):
        return ['cairo-devel', 'libsig++-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
       return {'': [x.replace ('-devel', '')
                    for x in self._get_build_dependencies ()
                    if 'tools::' not in x and 'cross/' not in x]}
    @context.subst_method
    def LDFLAGS (self):
#        return '-ldl ' + self.get_substitution_dict ()['LDFLAGS']
        return '-ldl -Wl,--as-needed'
    def configure_command (self):
        return ('''LDFLAGS='%(LDFLAGS)s' '''
                + target.AutoBuild.configure_command (self))
