from gub import repository
from gub import targetpackage

class Pjproject (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.downloads,
                                          url='http://www.pjsip.org/release/0.5.10.1/pjproject-0.5.10.1.tar.gz',
                                          version='0.5.10.1',
                                          strip_components=True))
    def force_sequential_build (self):
        return True
    def patch (self):
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/pjproject-install.patch')
    def configure_command (self):
#        return targetpackage.TargetBuild.configure_command (self).replace ('/configure', '/aconfigure')
        return (targetpackage.TargetBuild.configure_command (self).replace ('%(srcdir)s/configure', './aconfigure')
                + ' --disable-sound')
    def configure (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        targetpackage.TargetBuild.configure (self)
    def install_command (self):
        return (targetpackage.TargetBuild.install_command (self)
                + ' prefix=%(prefix_dir)s')
