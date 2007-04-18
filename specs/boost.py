import download
import misc
import targetpackage

# TODO: AutoToolSpec
class BjamBuildSpec (targetpackage.TargetBuildSpec):
    def patch (self):
        self.shadow_tree ('%(srcdir)s', '%(builddir)s')
    def get_substitution_dict (self, env={}):
        dict = targetpackage.TargetBuildSpec.get_substitution_dict (self, env)
        # When using GCC, boost ignores standard CC,CXX
        # settings, but looks at GCC,GXX.
        dict['GCC'] = dict['CC']
        dict['GXX'] = dict['CXX']
        dict['CFLAGS'] = 'boe'
        return dict
    def configure_command (self):
        return 'true'
    def compile_command (self):
# FIXME: get_substitution_dict is broken?
#'-sGCC=%(tool_prefix)s-gcc %(CFLAGS)s'
#'-sGXX=%(tool_prefix)s-g++ %(CFLAGS)s'
# FIXME: WTF, where has python_version gone?
#'-sPYTHON_VERSION=%(python_version)s'
# only static because dynamic libs fail on linux-64..?
#<runtime-link>static/dynamic
# --without-test because is only available as shared lib
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
        self.with (version='1.33.1', mirror=download.boost_1_33_1, format='bz2')
    def get_substitution_dict (self, env={}):
        dict = BjamBuildSpec.get_substitution_dict (self, env)
        # When using GCC, boost ignores standard CC,CXX
        # settings, but looks at GCC,GXX.
        dict['GCC'] = dict['CC']
        dict['GXX'] = dict['CXX']
        # WT-Bloody-F?
        dict['CFLAGS'] = '-DBOOST_PLATFORM_CONFIG=\\"boost/config/platform/linux.hpp\\"'
        return dict
    def license_file (self):
        return '%(srcdir)s/LICENSE_1_0.txt'

class Boost__linux_arm_softfloat (BjamBuildSpec):
    def configure_command (self):
        self.system ('''
cp -f boost/config/platform/linux.hpp boost/config/platform/linux-gnueabi.hpp
''')
