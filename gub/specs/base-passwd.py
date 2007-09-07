from gub import targetpackage
from gub import gubb

url='ftp://ftp.nl.debian.org/debian/pool/main/b/base-passwd/base-passwd_3.5.11.tar.gz'

# unneeded feeble attempt
from gub import context
class UnixBuildSpec (gubb.BuildSpec):
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    @context.subst_method
    def configure_command (self):
        return './configure --prefix=%(prefix_dir)s'

class Base_passwd (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        from gub import repository
        # FIXME: cannot parse debian balls
        self.ball_version = '3.5.11'
        self.with_tarball (mirror=url, version='')
    def get_subpackage_names (self):
        return ['']
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def configure_command (self):
        return (targetpackage.TargetBuildSpec.configure_command (self)
                .replace ('--config-cache', '--cache-file=%(builddir)s/config.cache'))
