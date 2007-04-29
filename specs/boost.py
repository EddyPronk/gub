import mirrors
import gub
import misc
import targetpackage
#
import os

# TODO: AutoToolSpec
class BjamBuildSpec (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        gub.append_target_dict (self, {'CFLAGS': ''})
    def get_substitution_dict (self, env={}):
        # FIXME: how to add settings to dict?
        dict = targetpackage.TargetBuildSpec.get_substitution_dict (self, env)
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
#'-sGCC=%(tool_prefix)sgcc %(CFLAGS)s
#'-sGXX=%(tool_prefix)sg++ %(CFLAGS)s

        return misc.join_lines ('''
bjam
'-sTOOLS=gcc'
'-sGCC=%(tool_prefix)sgcc -fPIC -DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
'-sGXX=%(tool_prefix)sg++ -fPIC -DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
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
--prefix=/usr
--exec-prefix=/usr
--libdir=/usr/lib
--includedir=/usr/include
''')
    def install_command (self):
        return (self.compile_command ()
                + ' install').replace ('=/usr', '=%(install_root)s/usr')

class Boost (BjamBuildSpec):
    def __init__ (self,settings):
        BjamBuildSpec.__init__ (self, settings)
        self.with (version='1.33.1', mirror=mirrors.boost_1_33_1, format='bz2')
        gub.change_target_dict (self, {'CFLAGS': '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'})
    def get_substitution_dict (self, env={}):
        dict = BjamBuildSpec.get_substitution_dict (self, env)
        dict['CFLAGS'] = '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
        return dict
    def license_file (self):
        return '%(srcdir)s/LICENSE_1_0.txt'
    def install (self):
        BjamBuildSpec.install (self)
        # Bjam `installs' header files by using symlinks to the source dir?
        for i in self.locate_files ('%(install_root)s/usr/include/boost',
                                    '*'):
            if os.path.islink (i):
                s = os.readlink (i)
                self.system ('''
rm %(i)s
cp %(s)s %(i)s
''',
                             locals ())
        cwd = os.getcwd ()
        os.chdir (self.expand ('%(install_root)s/usr/lib'))
        for i in self.locate_files ('%(install_root)s/usr/lib', 'libboost_*-s.a'):
            f = os.path.basename (i)
            os.symlink (f, f.replace ('-s.a', '.a'))
        os.chdir (cwd)
        
class Boost__linux_arm_softfloat (BjamBuildSpec):
    def configure_command (self):
        self.system ('''
cp -f boost/config/platform/linux.hpp boost/config/platform/linux-gnueabi.hpp
''')
