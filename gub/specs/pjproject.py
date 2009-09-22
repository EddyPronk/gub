from gub import target

class Pjproject (target.AutoBuild):
    source = 'http://www.pjsip.org/release/0.5.10.1/pjproject-0.5.10.1.tar.gz'
    parallel_build_broken = True
    srcdir_build_broken = True
    def patch (self):
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/pjproject-install.patch')
    def configure_flags (self):
        return (target.AutoBuild.configure_flags (self)
                + ' --disable-sound')
    def configure_binary (self):
        return './aconfigure'
    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + ' prefix=%(prefix_dir)s')
