from gub import targetbuild

class Cppunit (targetbuild.TargetBuild):
#    source = 'http://surfnet.dl.sourceforge.net/sourceforge/cppunit/cppunit-1.10.2.tar.gz'
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/cppunit/cppunit-1.12.1.tar.gz'

class Cppunit__mingw (Cppunit):
    def patch (self):
        Cppunit.patch (self)
        # old libtool barfs: no dll.a file
        # self.system ('mv -f %(cross_prefix)s/i686-mingw32/lib/libstdc++.dll.a %(system_prefix)s/lib/libstdc++.a')
        self.system ('mv %(system_prefix)s/lib/libstdc++.la %(system_prefix)s/lib/libstdc++.la- || :')
