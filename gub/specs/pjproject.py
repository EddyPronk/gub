from gub import target

class Pjproject (target.AutoBuild):
    source = 'http://www.pjsip.org/release/0.5.10.1/pjproject-0.5.10.1.tar.gz'
    def force_sequential_build (self):
        return True
    def patch (self):
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/pjproject-install.patch')
    def configure_command (self):
        return (target.AutoBuild.configure_command (self).replace ('%(srcdir)s/configure', './aconfigure')
                + ' --disable-sound')
    def configure (self):
        self.shadow ()
        target.AutoBuild.configure (self)
    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + ' prefix=%(prefix_dir)s')
