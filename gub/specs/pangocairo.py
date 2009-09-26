from gub import gnome
from gub import target
from gub.specs import pango

class Pangocairo (pango.Pango):
    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.26/2.26.3/sources/pango-1.24.4.tar.gz'
    dependencies = pango.Pango.dependencies + ['cairo-devel']
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
    configure_flags = (target.AutoBuild.configure_flags
                + ' --disable-rebuilds')

class Pangocairo__darwin__no_quartz_objective_c (Pangocairo):
    config_cache_overrides = Pangocairo.config_cache_overrides + '''
ac_cv_header_Carbon_Carbon_h=${ac_cv_header_Carbon_Carbon_h=no}
'''
