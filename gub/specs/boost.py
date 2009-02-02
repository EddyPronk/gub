from gub import loggedos
from gub import misc
from gub import target
#
import os

# TODO: AutoToolSpec
class BjamBuild (target.MakeBuild):
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        target.append_target_dict (self, {'CFLAGS': ''})
    def XXX_BROKEN_get_build_dependencies (self):
# the separately available boost-jam is terribly broken wrt building boost
# *** Stage: compile (boost, linux-64)
#invoking cd /home/janneke/vc/gub/target/linux-64/build/boost-1.33.1 &&  bjam '-sTOOLS=gcc' '-sGCC=x86_64-linux-gcc -fPIC -DBOOST_PLATFORM_CONFIG=\"boost/config/platform/linux.hpp\"' '-sGXX=x86_64-linux-g++ -fPIC -DBOOST_PLATFORM_CONFIG=\"boost/config/platform/linux.hpp\"' '-sNO_BZIP2=1' '-sNO_ZLIB=1' '-sBUILD=release <optimization>space <inlining>on <debug-symbols>off <runtime-link>static' '-sPYTHON_VERSION=2.4' '-scxxflags=-fPIC' --without-python --without-test --with-python-root=/dev/null --layout=system --builddir=/home/janneke/vc/gub/target/linux-64/build/boost-1.33.1 --with-python-root=/dev/null --prefix=/usr --exec-prefix=/usr --libdir=/usr/lib --includedir=/usr/include 
#Jamfile:114: in module scope
#rule unless unknown in module 
        return ['tools::boost-jam']
    def get_substitution_dict (self, env={}):
        # FIXME: how to add settings to dict?
        dict = target.AutoBuild.get_substitution_dict (self, env)
        dict['CFLAGS'] = ''
        return dict
    def compile_command (self):
# FIXME: WTF, where has python_version gone?
# only static because dynamic libs fail on linux-64..?
#<runtime-link>static/dynamic
# --without-test because is only available as shared lib

# FIXME: how to add settings to dict?
#'-sGCC=%(toolchain_prefix)sgcc %(CFLAGS)s
#'-sGXX=%(toolchain_prefix)sg++ %(CFLAGS)s

        return misc.join_lines ('''
bjam
'-sTOOLS=gcc'
'-sGCC=%(toolchain_prefix)sgcc -fPIC -DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
'-sGXX=%(toolchain_prefix)sg++ -fPIC -DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
'-sNO_BZIP2=1'
'-sNO_ZLIB=1'
'-sBUILD=release <optimization>space <inlining>on <debug-symbols>off <runtime-link>static'
'-sPYTHON_VERSION=2.4'
'-scxxflags=-fPIC'
--without-python
--without-test
--with-python-root=/dev/null
--layout=system
--builddir=%(builddir)s
--with-python-root=/dev/null
--prefix=%(prefix_dir)s
--exec-prefix=%(prefix_dir)s
--libdir=%(prefix_dir)s/lib
--includedir=%(prefix_dir)s/include
''')
    def install_command (self):
        return (self.compile_command ()
                + ' install').replace ('=%(prefix_dir)s', '=%(install_prefix)s')

class Boost (BjamBuild):
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost_1_33_1.tar.bz2'
    #source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost_1_34_1.tar.bz2'
    #source = 'http://surfnet.dl.sourceforge.net/sourceforge/boost/boost_1_34_1.tar.bz2'
    def __init__ (self, settings, source):
        BjamBuild.__init__ (self, settings, source)
        target.change_target_dict (self, {'CFLAGS': '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'})
    def get_substitution_dict (self, env={}):
        d = BjamBuild.get_substitution_dict (self, env)
        d['CFLAGS'] = '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
        d['PATH'] = '%(builddir)s:' + d['PATH']
        return d
    def stages (self):
        return misc.list_insert_before (BjamBuild.stages (self),
                                        'compile',
                                        ['build_bjam'])
    def build_bjam (self):
        # the separately available boost-jam is terribly broken wrt
        # building boost: build included bjam
        self.system ('cd %(builddir)s/tools/build/jam_src && sh build.sh gcc && mv bin.*/bjam %(builddir)s')
    def license_files (self):
        return ['%(srcdir)s/LICENSE_1_0.txt']
    def install (self):
        BjamBuild.install (self)
        # Bjam `installs' header files by using symlinks to the source dir?

        def add_plain_lib_names (logger, file):
            base = os.path.basename (file).replace ('-s.a', '.a')
            misc.symlink_in_dir (file, base)
        self.map_locate (add_plain_lib_names, '%(install_prefix)s/lib', 'libboost_*-s.a')

        def replace_links (logger, file):
            if os.path.islink (file):
                link = os.readlink (file)
                loggedos.system (logger, '''
rm %(file)s
cp %(link)s %(file)s
''' % locals ())
        self.map_locate (replace_links, '%(install_prefix)s/include/boost', '*')
        
class Boost__linux_arm_softfloat (BjamBuild):
    def shadow (self):
        BjamBuild.shadow (self)
        self.system ('''
cp -f boost/config/platform/linux.hpp boost/config/platform/linux-gnueabi.hpp
''')

class Boost__mingw (Boost):
    def compile_command (self):
        return (Boost.compile_command (self)
                .replace ('linux.hpp', 'win32.hpp'))
