from gub import target

class Dbus (target.AutoBuild):
    source = 'http://dbus.freedesktop.org/releases/dbus/dbus-1.2.14.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config',
                ]
    def config_cache_overrides (self, string):
        return string + '''
ac_cv_have_abstract_sockets=${ac_cv_have_abstract_sockets=yes}
'''
