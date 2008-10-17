from gub import targetbuild

class Db (targetbuild.TargetBuild):
    source = "http://download.oracle.com/berkeley-db/db-4.7.25.tar.gz"
    def patch (self):
        self.shadow_tree ('%(srcdir)s', targetbuild.TargetBuild.builddir (self))
    def configure_binary (self):
        return '../dist/configure'
    def builddir (self):
        return targetbuild.TargetBuild.builddir (self) + '/build_unix'

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
        self.system ('sed -ie s@HAVE_VXWORKS@__MINGW32__@ %(builddir)s/../os/os_mkdir.c')
        self.system ('sed -ie s@dbenv@env@ %(builddir)s/../os/os_yield.c')
    def configure (self):
        Db.configure (self)
        self.system ('echo "#undef fsync" >> %(builddir)s/db_config.h')
        self.system ('echo "#define fsync _commit" >> %(builddir)s/db_config.h')
        self.system ('sed -ie "s@[.]exe@@g" %(builddir)s/Makefile')
    def configure_command (self):
        return (Db.configure_command (self)
                + ' LDFLAGS=-lwsock32')
