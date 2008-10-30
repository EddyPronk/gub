from gub import target

class Db (target.AutoBuild):
    source = "http://download.oracle.com/berkeley-db/db-4.7.25.tar.gz"
    def cache_file (self):
        return '%(builddir)s/build_unix/config.cache'
    def configure_command (self):
        return 'cd build_unix && ../' + target.AutoBuild.configure_command (self)
    def autodir (self):
        return '%(srcdir)s/dist'
    def configure_binary (self):
        return 'dist/configure'
    def makeflags (self):
        return '-C build_unix'
    def configure (self):
        self.shadow ()
        self.system ('mkdir -p %(builddir)s/build_unix')
        target.AutoBuild.configure (self)
        self.file_sub ([('\(prefix\)docs', '\(prefix\)/share/doc/db'),
                        ('^	@', '	')],
                        '%(builddir)s/build_unix/Makefile')
    def install (self):
        target.AutoBuild.install (self)
        self.system ('rm -f %(install_prefix)s/lib/libdb.{a,so{,.a},la}')
        self.system ('cd %(install_prefix)s/lib && ln -s libdb-*.a libdb.a')
        self.system ('cd %(install_prefix)s/lib && ln -s libdb-*.la libdb.la')
        self.system ('cd %(install_prefix)s/lib && ln -s libdb-*.so libdb.so')

class Db__mingw (Db):
    patches = ['db-4.7.25-mingw.patch']
    # no libdb.dll without libwsock.dll
    # cannot find a free and functional libwsock.dll, though
    def xxget_build_dependencies (self):
        return ['libwsock32']
    def configure (self):
        Db.configure (self)
        self.system ('echo "#undef fsync" >> %(builddir)s/build_unix/db_config.h')
        self.system ('echo "#define fsync _commit" >> %(builddir)s/build_unix/db_config.h')
        self.file_sub ([('[.]exe', '')], '%(builddir)s/build_unix/Makefile')
        self.system ('''mkdir -p %(builddir)s/build_unix/arpa %(builddir)s/build_unix/net %(builddir)s/build_unix/netinet %(builddir)s/build_unix/sys
touch %(builddir)s/build_unix/net/uio.h
touch %(builddir)s/build_unix/sys/uio.h
touch %(builddir)s/build_unix/netinet/in.h
touch %(builddir)s/build_unix/netdb.h
touch %(builddir)s/build_unix/arpa/inet.h
''')
        self.file_sub ([('HAVE_VXWORKS', '__MINGW32__')],
                       '%(builddir)s/build_unix/../os/os_mkdir.c')
        self.file_sub ([('dbenv', 'env')], '%(builddir)s/os/os_yield.c')
    def configure_command (self):
        return (Db.configure_command (self)
                + ' LDFLAGS=-lwsock32')
    def install (self):
        target.AutoBuild.install (self)
        self.system ('rm -f %(install_prefix)s/{bin,lib}/libdb.{{,so,dll}{,.a},la}')
        self.system ('cd %(install_prefix)s/lib && cp libdb-*.a libdb.a')
        self.system ('cd %(install_prefix)s/lib && cp libdb-*.la libdb.la')
        if 'libwsock32' in self.get_build_dependencies ():
            self.system ('cd %(install_prefix)s/bin && cp libdb-*.dll libdb.dll')
            self.system ('cd %(install_prefix)s/lib && cp libdb-*.dll.a libdb.dll.a')
