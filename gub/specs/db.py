from gub import targetbuild

class Db (targetbuild.TargetBuild):
    source = "http://download.oracle.com/berkeley-db/db-4.7.25.tar.gz"
    def get_build_dependencies (self):
        return ['libwsock32']
    def patch (self):
        self.shadow_tree ('%(srcdir)s', targetbuild.TargetBuild.builddir (self))
    def configure_binary (self):
        return '../dist/configure'
    def builddir (self):
        return targetbuild.TargetBuild.builddir (self) + '/build_unix'
    def clean (self):
        targetbuild.TargetBuild.clean (self)
        if self.source.is_tracking ():
            # URG
            return
        self.system ('rm -rf ' + targetbuild.TargetBuild.builddir (self))
    def configure (self):
        targetbuild.TargetBuild.configure (self)
        self.system ('sed -i -e "s@/(prefix)docs@/(prefix)/share/doc/gb@" %(builddir)s/Makefile')
        self.system ('sed -i -e "s/^	@/	/" %(builddir)s/Makefile')
    def install (self):
        targetbuild.TargetBuild.install (self)
        self.system ('rm -f %(install_prefix)s/lib/libdb.{a,so{,.a},la}')
        self.system ('cd %(install_prefix)s/lib && ln -s libdb-*.a libdb.a')
        self.system ('cd %(install_prefix)s/lib && ln -s libdb-*.la libdb.la')
        self.system ('cd %(install_prefix)s/lib && ln -s libdb-*.so libdb.so')

class Db__mingw (Db):
    def patch (self):
        Db.patch (self)
        self.system ('''mkdir -p %(builddir)s/arpa %(builddir)s/net %(builddir)s/netinet %(builddir)s/sys
touch %(builddir)s/net/uio.h
touch %(builddir)s/sys/uio.h
touch %(builddir)s/netinet/in.h
touch %(builddir)s/netdb.h
touch %(builddir)s/arpa/inet.h
''')
        self.system ('sed -i -e s@HAVE_VXWORKS@__MINGW32__@ %(builddir)s/../os/os_mkdir.c')
        self.system ('sed -i -e s@dbenv@env@ %(builddir)s/../os/os_yield.c')
    def configure (self):
        Db.configure (self)
        self.system ('echo "#undef fsync" >> %(builddir)s/db_config.h')
        self.system ('echo "#define fsync _commit" >> %(builddir)s/db_config.h')
        self.system ('sed -i -e "s@[.]exe@@g" %(builddir)s/Makefile')
    def configure_command (self):
        return (Db.configure_command (self)
                + ' LDFLAGS=-lwsock32')
    def install (self):
        targetbuild.TargetBuild.install (self)
        self.system ('rm -f %(install_prefix)s/{bin,lib}/libdb.{{,so,dll}{,.a},la}')
        self.system ('cd %(install_prefix)s/bin && cp libdb-*.dll libdb.dll')
        self.system ('cd %(install_prefix)s/lib && cp libdb-*.a libdb.a')
        self.system ('cd %(install_prefix)s/lib && cp libdb-*.dll.a libdb.dll.a')
        self.system ('cd %(install_prefix)s/lib && cp libdb-*.la libdb.la')
