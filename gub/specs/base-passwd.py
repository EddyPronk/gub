from gub import targetbuild

class Base_passwd (targetbuild.AutoBuild):
    source = 'ftp://ftp.nl.debian.org/debian/pool/main/b/base-passwd/base-passwd_3.5.11.tar.gz'
    def get_subpackage_names (self):
        return ['']
    def def configure (self):
        self.shadow ()
        targetbuild.AutoBuild.configure (self)
    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                .replace ('--config-cache', '--cache-file=%(builddir)s/config.cache'))
