from gub import misc
from gub import targetbuild

class Redland (targetbuild.AutoBuild):
    source = 'http://download.librdf.org/source/redland-1.0.8.tar.gz'
    def get_build_dependencies (self):
        return ['rasqal-devel', 'sqlite-devel']
    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                + misc.join_lines ('''
 --without-mysql
 --without-postgresql
'''))
    def config_script (self):
        return 'redland-config'

class Redland__mingw (Redland):
    patches = ['redland-1.0.8-mingw.patch']
    def patch (self):
        Redland.patch (self)
        self.file_sub ([
                ('#define HAVE_BDB_HASH 1', '/* undef HAVE_BDB_HASH */'),
                ('#define HAVE_MYSQL 1', '/* undef HAVE_MYSQL */'),
                ('#define STORAGE_MYSQL 1', '/* undef STORAGE_MYSQL */'),
                ], '%(srcdir)s/librdf/win32_rdf_config.h')
        '''
i686-mingw32-gcc -mwindows -mms-bitfields -DLIBRDF_INTERNAL=1 -g -O2 -DLIBRDF_INTERNAL=1 -g -O2 -o .libs/redland-db-upgrade.exe db_upgrade.o  -L/home/janneke/vc/gub/target/mingw/root/usr/lib -L/home/janneke/vc/gub/target/mingw/root/usr/bin -L/home/janneke/vc/gub/target/mingw/root/usr/lib/w32api ../librdf/.libs/librdf.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/librasqal.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libpcre.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libgmp.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libraptor.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libcurl.dll.a -lwldap32 /home/janneke/vc/gub/target/mingw/root/usr/lib/libxslt.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libxml2.dll.a -lws2_32 /home/janneke/vc/gub/target/mingw/root/usr/lib/libsqlite3.dll.a  -L/home/janneke/vc/gub/target/mingw/root/usr/lib
db_upgrade.o: In function `main':
/home/janneke/vc/gub/target/mingw/src/redland-1.0.8/utils/db_upgrade.c:59: undefined reference to `_librdf_heuristic_gen_name'
collect2: ld returned 1 exit status
make[1]: *** [redland-db-upgrade.exe] Fout 1
make[1]: *** Wachten op onvoltooide taken...
i686-mingw32-gcc -mwindows -mms-bitfields -DLIBRDF_INTERNAL=1 -g -O2 -DLIBRDF_INTERNAL=1 -g -O2 -o .libs/rdfproc.exe rdfproc.o  -L/home/janneke/vc/gub/target/mingw/root/usr/lib -L/home/janneke/vc/gub/target/mingw/root/usr/bin -L/home/janneke/vc/gub/target/mingw/root/usr/lib/w32api ../librdf/.libs/librdf.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/librasqal.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libpcre.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libgmp.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libraptor.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libcurl.dll.a -lwldap32 /home/janneke/vc/gub/target/mingw/root/usr/lib/libxslt.dll.a /home/janneke/vc/gub/target/mingw/root/usr/lib/libxml2.dll.a -lws2_32 /home/janneke/vc/gub/target/mingw/root/usr/lib/libsqlite3.dll.a  -L/home/janneke/vc/gub/target/mingw/root/usr/lib
Info: resolving _librdf_version_string by linking to __imp__librdf_version_string (auto-import)
Info: resolving _librdf_short_copyright_string by linking to __imp__librdf_short_copyright_string (auto-importrdfproc.o: In function `main':
/home/janneke/vc/gub/target/mingw/src/redland-1.0.8/utils/rdfproc.c:302: undefined reference to `_librdf_new_hash'
/home/janneke/vc/gub/target/mingw/src/redland-1.0.8/utils/rdfproc.c:303: undefined reference to `_librdf_hash_open'
/home/janneke/vc/gub/target/mingw/src/redland-1.0.8/utils/rdfproc.c:617: undefined reference to `_librdf_hash_from_string'
/home/janneke/vc/gub/target/mingw/src/redland-1.0.8/utils/rdfproc.c:447: undefined reference to `_librdf_get_storage_factory'
/home/janneke/vc/gub/target/mingw/src/redland-1.0.8/utils/rdfproc.c:1186: undefined reference to `_librdf_heuristic_is_blank_node'
/home/janneke/vc/gub/target/mingw/src/redland-1.0.8/utils/rdfproc.c:1187: undefined reference to `_librdf_heuristic_get_blank_node'
'''
        self.file_sub ([('^(SUBDIRS =.*) utils ', r'\1 ')],
                       '%(srcdir)s/Makefile.am')
        self.file_sub ([('^(SUBDIRS =.*) utils ', r'\1 ')],
                       '%(srcdir)s/Makefile.in')
