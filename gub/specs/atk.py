from gub import context
from gub import target

class Atk (target.AutoBuild):
    source = 'ftp://ftp.gnome.org/pub/GNOME/sources/atk/1.25/atk-1.25.2.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'glib-devel']
#    @context.subst_method
#    def LD_LIBRARY_PATH (self):
#        # UGH. glib-2.0.m4's configure snippet compiles and runs a
#        # program linked against glib; so it needs LD_LIBRARY_PATH (or
#        # a configure-time-only -Wl,-rpath, -Wl,%(system_prefix)s/lib
#        return '%(system_prefix)s/lib'
    def configure_command (self):
        # UGH. glib-2.0.m4's configure snippet compiles and runs a
        # program linked against glib; so it needs LD_LIBRARY_PATH (or
        # a configure-time-only -Wl,-rpath, -Wl,%(system_prefix)s/lib
        return (target.AutoBuild.configure_command (self)
                + ''' LDFLAGS='-Wl,-rpath -Wl,%(system_prefix)s/lib %(rpath)s %(rpath)s' ''')

