from gub import mirrors
from gub import build
from gub import misc
from gub import targetbuild
#
import os

# TODO: AutoToolSpec
class BjamBuild (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        build.append_target_dict (self, {'CFLAGS': ''})
    def get_substitution_dict (self, env={}):
        # FIXME: how to add settings to dict?
        dict = targetbuild.TargetBuild.get_substitution_dict (self, env)
        dict['CFLAGS'] = ''
        return dict
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def configure_command (self):
        return 'true'
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
    def __init__ (self,settings):
        BjamBuild.__init__ (self, settings, source)
    source = mirrors.with_template (name='boost', version='1.33.1', mirror=mirrors.boost_1_33_1, format='bz2')
        build.change_target_dict (self, {'CFLAGS': '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'})
    def get_substitution_dict (self, env={}):
        dict = BjamBuild.get_substitution_dict (self, env)
        dict['CFLAGS'] = '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
        return dict
    def license_file (self):
        return '%(srcdir)s/LICENSE_1_0.txt'
    def install (self):
        BjamBuild.install (self)
        # Bjam `installs' header files by using symlinks to the source dir?
        for i in self.locate_files ('%(install_prefix)s/include/boost',
                                    '*'):
            if os.path.islink (i):
                s = os.readlink (i)
                self.system ('''
rm %(i)s
cp %(s)s %(i)s
''',
                             locals ())
        cwd = os.getcwd ()
        os.chdir (self.expand ('%(install_prefix)s/lib'))
        for i in self.locate_files ('%(install_prefix)s/lib', 'libboost_*-s.a'):
            f = os.path.basename (i)
            os.symlink (f, f.replace ('-s.a', '.a'))
        os.chdir (cwd)
        
class Boost__linux_arm_softfloat (BjamBuild):
    def configure_command (self):
        self.system ('''
cp -f boost/config/platform/linux.hpp boost/config/platform/linux-gnueabi.hpp
''')
