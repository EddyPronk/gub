from gub import build
from gub import tools

class M4__tools (tools.AutoBuild):
    source = 'ftp://ftp.gnu.org/pub/gnu/m4/m4-1.4.12.tar.gz'
    def config_cache_settings (self):
        return self.config_cache_overrides ('')
    def config_cache_overrides (self, string):
        # avoid using stray libsigsegv
        return string + '\ngl_cv_lib_sigsegv=${gl_cv_lib_sigsegv=no}\n'
    def wrap_executables (self):
        # no dynamic executables [other than /lib:libc]
        pass
