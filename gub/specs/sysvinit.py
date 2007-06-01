from gub import targetpackage
from gub import repository

url = 'ftp://ftp.cistron.nl/pub/people/miquels/sysvinit/sysvinit-2.86.tar.gz'

class Sysvinit (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads, url))
    def get_subpackage_names (self):
        return ['']
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def configure_command (self):
        return 'true'
    def makeflags (self):
        return 'CC=%(tool_prefix)sgcc ROOT=%(install_root)s'
    def compile_command (self):
        return 'cd %(builddir)s/src && make %(makeflags)s'
    def install_command (self):
        from gub import misc
        # FIXME: cannot do these as self.system () in install () as
        # install will rm -rf %(install_root)s as first command
        # install_clean/install_install?
        return misc.join_lines ('''
mkdir -p %(install_root)s/bin &&
mkdir -p %(install_root)s/sbin &&
mkdir -p %(install_root)s/usr/bin &&
mkdir -p %(install_root)s/usr/include &&
mkdir -p %(install_root)s/usr/share/man/man1 &&
mkdir -p %(install_root)s/usr/share/man/man5 &&
mkdir -p %(install_root)s/usr/share/man/man8 &&
cd %(builddir)s/src && fakeroot make install %(makeflags)s
''')
    def license_file (self):
        return '%(srcdir)s/doc/Install'
