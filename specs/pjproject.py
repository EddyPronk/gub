import repository
import targetpackage

class Pjproject (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.TarBall (self.settings.mirrorss,
                                          url='http://www.pjsip.org/release/0.5.10.1/pjproject-0.5.10.1.tar.gz',
                                          version='0.5.10.1',
                                          strip_components=True))
        # FIXME: broken for make -j2, why does broken_for_distcc not handle?
        self.settings.cpu_count_str = '1'
    def broken_for_distcc (self):
        return True
    def patch (self):
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/pjproject-install.patch')
    def configure_command (self):
#        return targetpackage.TargetBuildSpec.configure_command (self).replace ('/configure', '/aconfigure')
        return (targetpackage.TargetBuildSpec.configure_command (self).replace ('%(srcdir)s/configure', './aconfigure')
                + ' --disable-sound')
    def configure (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
        targetpackage.TargetBuildSpec.configure (self)
    def install_command (self):
        return (targetpackage.TargetBuildSpec.install_command (self)
                + ' prefix=/usr')
