from gub import target

class Dbus (target.AutoBuild):
    source = 'http://dbus.freedesktop.org/releases/dbus/dbus-1.2.14.tar.gz'
    dependencies = ['tools::automake', 'tools::pkg-config',
                ]
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
ac_cv_have_abstract_sockets=${ac_cv_have_abstract_sockets=yes}
'''
