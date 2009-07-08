from gub import target

class Lash (target.AutoBuild):
    source = 'http://www.very-clever.com/download/nongnu/lash/lash-0.6.0~rc2.tar.bz2'
    patches = ['lash-0.6.0.rc2.patch']
    def _get_build_dependencies (self):
        return ['tools::automake', 'tools::pkg-config',
                'e2fsprogs-devel',
                'dbus-devel',
                'jack-devel',
                ]
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + '--without-python')
        # either that, or
        # + 'CPPFLAGS="-I%(system_prefix)s/include `python-config --cflags`"'
        # + 'LDFLAGS="`python-config --ldflags`"')
