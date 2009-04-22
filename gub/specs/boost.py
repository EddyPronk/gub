import os
#
from gub import context
from gub import loggedos
from gub import misc
from gub import target
from gub import tools

def add_plain_lib_names (logger, file):
    base = (os.path.basename (file)
            .replace ('-mt.a', '.a')
            .replace ('-s.a', '.a')
            .replace ('-mt.so', '.so')
            .replace ('-s.so', '.so'))
    misc.symlink_in_dir (file, base)

def replace_links (logger, file):
    if os.path.islink (file):
        link = os.readlink (file)
        loggedos.system (logger, '''
rm %(file)s
cp %(link)s %(file)s
''' % locals ())

class Boost (target.BjamBuild_v2):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost_1_38_0.tar.bz2'
    def _get_build_dependencies (self):
# the separately available boost-jam is terribly broken wrt building boost
# *** Stage: compile (boost, linux-64)
#invoking cd /home/janneke/vc/gub/target/linux-64/build/boost-1.33.1 &&  bjam '-sTOOLS=gcc' '-sGCC=x86_64-linux-gcc -fPIC -DBOOST_PLATFORM_CONFIG=\"boost/config/platform/%(target_os)s.hpp\"' '-sGXX=x86_64-linux-g++ -fPIC -DBOOST_PLATFORM_CONFIG=\"boost/config/platform/%(target_os)s.hpp\"' '-sNO_BZIP2=1' '-sNO_ZLIB=1' '-sBUILD=release <optimization>space <inlining>on <debug-symbols>off <runtime-link>static' '-sPYTHON_VERSION=2.4' '-scxxflags=-fPIC' --without-python --without-test --with-python-root=/dev/null --layout=system --builddir=/home/janneke/vc/gub/target/linux-64/build/boost-1.33.1 --with-python-root=/dev/null --prefix=/usr --exec-prefix=/usr --libdir=/usr/lib --includedir=/usr/include 
#Jamfile:114: in module scope
#rule unless unknown in module 
        return []
    def stages (self):
        return misc.list_insert_before (target.BjamBuild_v2.stages (self),
                                        'compile',
                                        ['build_bjam'])
    def build_bjam (self):
        self.system ('cd %(builddir)s/tools/jam/src && CC=gcc sh build.sh gcc && mv bin.*/bjam %(builddir)s')
    def boost_modules (self):
        return [
            'date_time',
            'filesystem',
            'function_types',
            #'graph',
            'iostreams',
            #'math',
            'program_options',
            #'python',
            'regex',
            'serialization',
            'signals',
            'system',
            #'test',
            'thread',
            #'wave'
            ]
    def compile_command (self):
        return (target.BjamBuild_v2.compile_command (self)
                .replace ('bjam ', '%(builddir)s/bjam ')
                + ' -sNO_BZIP2=1'
                + ' -sNO_ZLIB=1'
                + ' --with-'.join ([''] + self.boost_modules ()))
    def license_files (self):
        return ['%(srcdir)s/LICENSE_1_0.txt']
    def install (self):
        target.BjamBuild_v2.install (self)
        # Bjam `installs' header files by using symlinks to the source dir?
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-mt.a')
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-mt.so')
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-s.a')
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-s.so')
        self.map_locate (replace_links, '%(install_prefix)s/include/boost', '*')
        
class Boost__freebsd__x86 (Boost):
    patches = ['boost-1.38.0-freebsd4.patch']
    def compile_command (self):
        return (Boost.compile_command (self)
                .replace ('--with-serialization', ''))

class UGLYFIXBoost__mingw (Boost):
    @context.subst_method
    def target_os (self):
        return 'windows'
    ## UGH, function in boost-1.38 breaks badly
    ## the easy fix is to revert to 1.33.1
    '''
/home/janneke/vc/gub/target/mingw/root/usr/include/boost/function/function_template.hpp:965: error: declaration of 'class R'
/home/janneke/vc/gub/target/mingw/root/usr/include/boost/function/function_template.hpp:652: error:  shadows template parm 'class R'
/home/janneke/vc/gub/target/mingw/root/usr/include/boost/function/function_template.hpp:979: error: declaration of 'class R'
/home/janneke/vc/gub/target/mingw/root/usr/include/boost/function/function_template.hpp:652: error:  shadows template parm 'class R'
/home/janneke/vc/gub/target/mingw/root/usr/include/boost/function/function_template.hpp:983: error: cannot define member function 'boost::function0<R>::operator()' within 'boost::function0<R
>'
'''
    def __init__ (self, settings, source):
        Boost.__init__ (self, settings, source)
        self.function_source = repository.get_repository_proxy (self.settings.downloads, 'http://lilypond.org/download/gub-sources/boost-function/boost-function-1.34.1.tar.gz?strip=0')
    def connect_command_runner (self, runner):
        printf ('FIXME: deferred workaround')
        if (runner):
            self.function_source.connect_logger (runner.logger)
        return Boost.connect_command_runner (self, runner)
    def download (self):
        Boost.download (self)
        self.function_source.download ()
    def install (self):
        Boost.install (self)
        self.install_function ()
    def install_function (self):
        function_dir = self.expand ('%(install_prefix)s/include')
        def defer (logger):
            self.function_source.update_workdir (function_dir)
        self.func (defer)

class BjamBuild_v1 (target.MakeBuild):
    @context.subst_method
    def CFLAGS (self):
        return ''
    def compile_command (self):
        return misc.join_lines ('''
bjam
-q
'-sTOOLS=gcc'
'-sGCC=%(toolchain_prefix)sgcc -fPIC -DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
'-sGXX=%(toolchain_prefix)sg++ -fPIC -DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
'-sBUILD=release <optimization>space <inlining>on <debug-symbols>off <runtime-link>static'
'-sPYTHON_VERSION=2.4'
'-scxxflags=-fPIC'
--layout=system
--builddir=%(builddir)s
--prefix=%(prefix_dir)s
--exec-prefix=%(prefix_dir)s
--libdir=%(prefix_dir)s/lib
--includedir=%(prefix_dir)s/include
--verbose
''')
    def install_command (self):
        return (self.compile_command ()
                + ' install').replace ('=%(prefix_dir)s', '=%(install_prefix)s')

class Boost_v1 (BjamBuild_v1):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost_1_33_1.tar.bz2'
    def stages (self):
        return misc.list_insert_before (BjamBuild_v1.stages (self),
                                        'compile',
                                        ['build_bjam'])
    def build_bjam (self):
        # the separately available boost-jam is terribly broken wrt
        # building boost: build included bjam
        self.system ('cd %(builddir)s/tools/build/jam_src && CC=gcc sh build.sh gcc && mv bin.*/bjam %(builddir)s')
    def license_files (self):
        return ['%(srcdir)s/LICENSE_1_0.txt']
    def boost_modules (self):
        return [
            'date_time',
            'filesystem',
            'function_types',
            #'graph',
            'iostreams',
            #'math',
            'program_options',
            #'python',
            'regex',
            'serialization',
            'signals',
            'system',
            #'test',
            'thread',
            #'wave'
            ]
    def compile_command (self):
        return (BjamBuild_v1.compile_command (self)
                .replace ('bjam ', '%(builddir)s/bjam ')
                + ' -sNO_BZIP2=1'
                + ' -sNO_ZLIB=1'
                + ' --with-'.join ([''] + self.boost_modules ()))
    def install (self):
        BjamBuild_v1.install (self)
        # Bjam `installs' header files by using symlinks to the source dir?
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-mt.a')
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-mt.so')
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-s.a')
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-s.so')
        self.map_locate (replace_links, '%(install_prefix)s/include/boost', '*')

class Boost__mingw (Boost_v1):
    def compile_command (self):
        return (Boost_v1.compile_command (self)
                .replace ('linux.hpp', 'win32.hpp'))

class Boost__tools (tools.BjamBuild_v2, Boost):
    @context.subst_method
    def CXX (self):
        return 'g++'
    def stages (self):
        return Boost.stages (self)
    def build_bjam (self):
        # the separately available boost-jam is terribly broken wrt
        # building boost: build included bjam
        self.system ('cd %(builddir)s/tools/jam/src && CC=gcc sh build.sh gcc && mv bin.*/bjam %(builddir)s')
    def compile_command (self):
        return (tools.BjamBuild_v2.compile_command (self)
                .replace ('bjam ', '%(builddir)s/bjam ')
                + ' -sNO_BZIP2=1'
                + ' -sNO_ZLIB=1'
                + ' --with-'.join ([''] + Boost.boost_modules (self)))
    def install (self):
        tools.BjamBuild_v2.install (self)
        # Bjam `installs' header files by using symlinks to the source dir?
        self.map_locate (add_plain_lib_names, '%(install_root)s%(system_prefix)s/lib', 'libboost_*-mt.a')
        self.map_locate (add_plain_lib_names, '%(install_root)s%(system_prefix)s/lib', 'libboost_*-mt.so')
        self.map_locate (add_plain_lib_names, '%(install_root)s%(system_prefix)s/lib', 'libboost_*-s.a')
        self.map_locate (add_plain_lib_names, '%(install_root)s%(system_prefix)s/lib', 'libboost_*-s.so')
        self.map_locate (replace_links, '%(install_root)s%(system_prefix)s/include/boost', '*')
