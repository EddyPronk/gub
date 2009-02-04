from gub.specs import pango

class Pangocairo (pango.Pango):
#    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.22/2.22.0/sources/pango-1.20.0.tar.bz2'
    source = 'http://ftp.acc.umu.se/pub/GNOME/platform/2.25/2.25.5/sources/pango-1.22.4.tar.gz'
    patches = pango.Pango.patches #['pango-1.20-substitute-env.patch']
    def _get_build_dependencies (self):
        return pango.Pango.get_build_dependencies (self) + ['cairo-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
       return {'': [x.replace ('-devel', '')
                    for x in self._get_build_dependencies ()
                    if 'tools::' not in x and 'cross/' not in x]}
    def get_conflict_dict (self):
        return {'': ['pango', 'pango-devel', 'pango-doc'], 'devel': ['pango', 'pango-devel', 'pango-doc'], 'doc': ['pango', 'pango-devel', 'pango-doc'], 'runtime': ['pango', 'pango-devel', 'pango-doc']}
