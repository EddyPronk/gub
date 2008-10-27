from gub import loggedos
from gub import misc
from gub import targetbuild
#
import os

# TODO: AutoToolSpec
class BjamBuild (targetbuild.MakeBuild):
    def __init__ (self, settings, source):
        targetbuild.AutoBuild.__init__ (self, settings, source)
        targetbuild.append_target_dict (self, {'CFLAGS': ''})
    def get_substitution_dict (self, env={}):
        # FIXME: how to add settings to dict?
        dict = targetbuild.AutoBuild.get_substitution_dict (self, env)
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
    def __init__ (self, settings, source):
        BjamBuild.__init__ (self, settings, source)
        targetbuild.change_target_dict (self, {'CFLAGS': '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'})
    def get_substitution_dict (self, env={}):
        dict = BjamBuild.get_substitution_dict (self, env)
        dict['CFLAGS'] = '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
        return dict
    def license_files (self):
        return ['%(srcdir)s/LICENSE_1_0.txt']
    def install (self):
        BjamBuild.install (self)
        # Bjam `installs' header files by using symlinks to the source dir?

        def add_plain_lib_names (logger, file):
            os.symlink (file, file.replace ('-s.a', '.a'))
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
