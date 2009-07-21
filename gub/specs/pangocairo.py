from gub.specs import pango

class Pangocairo (pango.Pango):
    #source = 'http://ftp.acc.umu.se/pub/GNOME/platform/2.25/2.25.5/sources/pango-1.22.4.tar.gz'
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.26/2.26.3/sources/pango-1.24.4.tar.gz'
    def _get_build_dependencies (self):
        return pango.Pango._get_build_dependencies (self) + ['cairo-devel']
    def get_conflict_dict (self):
        return {'': ['pango', 'pango-devel', 'pango-doc'], 'devel': ['pango', 'pango-devel', 'pango-doc'], 'doc': ['pango', 'pango-devel', 'pango-doc'], 'runtime': ['pango', 'pango-devel', 'pango-doc']}

class Pangocairo__mingw (Pangocairo):
    # FIXME: cut and paste Pango__mingw
    def create_config_files (self, prefix='/usr'):
        Pangocairo.create_config_files (self, prefix)
        etc = self.expand ('%(install_root)s/%(prefix)s/etc/pango', locals ())
        self.dump ('''${PANGO_PREFIX}/lib/pango/${PANGO_MODULE_VERSION}/modules/pango-basic-win32${PANGO_SO_EXTENSION} BasicScriptEngineWin32 PangoEngineShape PangoRenderWin32 common:
''', '%(etc)s/pango.modules', env=locals (), mode='a')
        Pangocairo.fix_config_files (self, prefix)

class Pangocairo__darwin (Pangocairo):
    def config_cache_overrides (self, string):
        # compiling with Carbon requires -xobjective-c flag,
        # which GUB currently not has
        #    i686-apple-darwin8-gcc: language objective-c not recognized
        # So, try without Carbon before changing GCC.
        return string + '''
ac_cv_header_Carbon_Carbon_h=${ac_cv_header_Carbon_Carbon_h=no}
'''
