from gub import gnome
from gub import target
from gub.specs import pango

class Pangocairo (pango.Pango):
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

class Pangocairo__darwin (Pangocairo):
    def configure (self):
        Pangocairo.configure (self)
        self.file_sub ([('nmedit', '%(target_architecture)s-nmedit')],
                       '%(builddir)s/libtool')
    def install (self):
        Pangocairo.install (self)                
        # FIXME: PANGO needs .so, NOT .dylib?
        self.dump ('''
set PANGO_SO_EXTENSION=.so
''', '%(install_prefix)s/etc/relocate/pango.reloc', env=locals (), mode='a')

class Pangocairo__darwin__no_quartz_objective_c (Pangocairo):
    config_cache_overrides = Pangocairo.config_cache_overrides + '''
ac_cv_header_Carbon_Carbon_h=${ac_cv_header_Carbon_Carbon_h=no}
'''
