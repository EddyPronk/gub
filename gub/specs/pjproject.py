from gub import target

class Pjproject (target.AutoBuild):
    source = 'http://www.pjsip.org/release/0.5.10.1/pjproject-0.5.10.1.tar.gz'
    parallel_build_broken = True
    srcdir_build_broken = True
    def patch (self):
        self.system ('cd %(srcdir)s && patch -p0 < %(patchdir)s/pjproject-install.patch')
    configure_flags = (target.AutoBuild.configure_flags
                + ' --disable-sound')
    def configure_binary (self):
        return './aconfigure'
    install_command = (target.AutoBuild.install_command
                + ' prefix=%(prefix_dir)s')
