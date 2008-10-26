from gub import build
from gub import context
from gub import loggedos
from gub import misc
from gub import targetbuild

class Libicu (targetbuild.TargetBuild):
    source = 'http://download.icu-project.org/files/icu4c/3.8.1/icu4c-3_8_1-src.tgz'
    #http://download.icu-project.org/files/icu4c/4.0/icu4c-4_0-src.tgz
    patches = ['libicu-3.8.1-cross.patch']
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        source._version = '3.8.1'
    def stages (self):
        return misc.list_insert_before (targetbuild.TargetBuild.stages (self),
                                        'configure',
                                        ['configure_native', 'compile_native'])
    def configure_binary (self):
        return '%(srcdir)s/source/configure'
    def makeflags (self):
        return misc.join_lines ('''
BINDIR_FOR_BUILD='$(BINDIR)-native'
LIBDIR_FOR_BUILD='$(LIBDIR)-native'
PKGDATA_INVOKE_OPTS="TARGET='lib\$\$(LIBNAME).so' BINDIR_FOR_BUILD='\$\$(BINDIR)-native' LIBDIR_FOR_BUILD='\$\$(LIBDIR)-native'"
''')
    @context.subst_method
    def makeflags_native (self):
        return misc.join_lines ('''
BINDIR='$(top_builddir)/bin-native'
LIBDIR='$(top_builddir)/lib-native'
PKGDATA_INVOKE_OPTS="BINDIR='\$\$(top_builddir)/bin-native' LIBDIR='\$\$(top_builddir)/lib-native'"
''')
    def compile_native (self):
        targetbuild.TargetBuild.compile_native (self)
        def rm (logger, file):
            loggedos.system (logger, 'rm -f %(file)s' % locals ())
        # ugh, should add misc.find () as map_find () to context interface
        # self.map_locate (rm, '%(builddir)s', '*.so.*')
        # self.map_locate (rm, '%(builddir)s', '*.so')
        self.map_locate (rm, '%(builddir)s', '*.o')
        self.get_substitution_dict = misc.bind_method (targetbuild.TargetBuild.get_substitution_dict, self)

class Libicu__mingw (Libicu):
    patches = Libicu.patches + ['libicu-3.8.1-uintptr-t.patch', 'libicu-3.8.1-cross-mingw.patch']
    def compile_native (self):
        Libicu.compile_native (self)
        self.system ('cd %(builddir)s/bin-native && mv pkgdata pkgdata.bin')
        self.dump ('''\
#! /bin/sh
dir=$(dirname $0)
if test "$dir" = "."; then
   dir=$(dirname $(which $0))
fi
$dir/$(basename $0).bin "$@" | sed -e 's/lib$(LIBNAME).so/$(LIBNAME).dll/g'
''',
             '%(builddir)s/bin-native/pkgdata',
                   permissions=0755)
