from gub import target

class Sysvinit (target.MakeBuild):
    source = 'ftp://ftp.cistron.nl/pub/people/miquels/sysvinit/sysvinit-2.86.tar.gz'
    subpackage_names = ['']
    make_flags = 'CC=%(toolchain_prefix)sgcc ROOT=%(install_root)s'
    compile_command = 'cd %(builddir)s/src && make %(make_flags)s'
    def install (self):
        fakeroot_cache = self.builddir () + '/fakeroot.cache'
        self.fakeroot (self.expand (self.settings.fakeroot, locals ()))
        target.AutoBuild.install (self)
        from gub import misc
        # FIXME: cannot do these as self.system () in install () as
        # install will rm -rf %(install_root)s as first command
        # install_clean/install_install?
    install_command = misc.join_lines ('''
mkdir -p %(install_root)s/bin &&
mkdir -p %(install_root)s/sbin &&
mkdir -p %(install_prefix)s/bin &&
mkdir -p %(install_prefix)s/include &&
mkdir -p %(install_prefix)s/share/man/man1 &&
mkdir -p %(install_prefix)s/share/man/man5 &&
mkdir -p %(install_prefix)s/share/man/man8 &&
cd %(builddir)s/src && fakeroot make install %(make_flags)s &&
find %(install_root)s/bin %(install_root)s/sbin %(install_prefix)s/bin -type f -o -type l | grep -Ev 'sbin/(tel|)init$' | xargs -I'{}' mv '{}' '{}'.sysvinit
''')
    def license_files (self):
        return ['%(srcdir)s/doc/Install']
