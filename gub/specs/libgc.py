from gub import target

class Libgc (target.AutoBuild):
    source = 'http://www.hpl.hp.com/personal/Hans_Boehm/gc/gc_source/gc-7.1.tar.gz'

class Libgc__freebsd (Libgc):
    def makeflags (self):
        return 'THREADDLLIBS=-pthread'

class Libgc__freebsd__x86 (Libgc__freebsd):
    source = 'http://www.hpl.hp.com/personal/Hans_Boehm/gc/gc_source/gc6.8.tar.gz&version=6.8'
    #patches = ['libgc-6.8-freebsd-x86_64.patch']

class Libgc__mingw (Libgc):
    source = 'http://www.hpl.hp.com/personal/Hans_Boehm/gc/gc_source/gc6.8.tar.gz&version=6.8'
    #patches = ['libgc-6.8-freebsd-x86_64.patch']
