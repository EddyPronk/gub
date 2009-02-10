from gub.specs import pango

class Pangocairo (pango.Pango):
    source = 'http://ftp.acc.umu.se/pub/GNOME/platform/2.25/2.25.5/sources/pango-1.22.4.tar.gz'
    def _get_build_dependencies (self):
        return pango.Pango._get_build_dependencies (self) + ['cairo-devel']
    def get_conflict_dict (self):
        return {'': ['pango', 'pango-devel', 'pango-doc'], 'devel': ['pango', 'pango-devel', 'pango-doc'], 'doc': ['pango', 'pango-devel', 'pango-doc'], 'runtime': ['pango', 'pango-devel', 'pango-doc']}
