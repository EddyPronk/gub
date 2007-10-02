from gub import repository
from gub import targetbuild

class Pjproject (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_vc (repository.TarBall (self.settings.downloads,
                                          url='http://www.pjsip.org/release/0.5.10.1/pjproject-0.5.10.1.tar.gz',
                                          version='0.5.10.1',
                                          strip_components=True))
    def force_sequential_build (self):
        return True
    def patch (self):
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/pjproject-install.patch')
    def configure_command (self):
#        return targetbuild.TargetBuild.configure_command (self).replace ('/configure', '/aconfigure')
        return (targetbuild.TargetBuild.configure_command (self).replace ('%(srcdir)s/configure', './aconfigure')
                + ' --disable-sound')
    def configure (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        targetbuild.TargetBuild.configure (self)
    def install_command (self):
        return (targetbuild.TargetBuild.install_command (self)
                + ' prefix=%(prefix_dir)s')
