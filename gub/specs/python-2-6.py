from gub import target
from gub import tools
from gub.specs import python

class Python_2_6 (python.Python):
    source = 'http://www.python.org/ftp/python/2.6.4/Python-2.6.4.tar.bz2'
    dependencies = [
        'db-devel',
        'expat-devel',
        'zlib-devel',
        'tools::python-2-6'
        ]
    patches = [
        'python-2.6.4.patch',
        'python-configure.in-posix.patch&strip=0',
        'python-2.6.4-configure.in-sysname.patch',
        'python-2.4.2-configure.in-sysrelease.patch',
        'python-2.4.2-setup.py-import.patch&strip=0',
        'python-2.6.4-setup.py-cross_root.patch',
#        'python-2.4.2-fno-stack-protector.patch',
#        'python-2.4.5-python-2.6.patch',
        'python-2.4.5-native.patch',
#        'python-2.4.5-db4.7.patch',
        'python-2.6.4-configure.in-cross.patch',
        'python-2.6.4-include-pc.patch',
        ]
    config_cache_overrides = python.Python.config_cache_overrides + '''
ac_cv_have_chflags=no
ac_cv_have_lchflags=no
ac_cv_py_format_size_t=no
'''
    so_modules = [
        '_struct',
        'datetime',
        'itertools',
        'time',
        ]

class Python_2_6__mingw (python.Python__mingw):
    source = Python_2_6.source
    patches = Python_2_6.patches + [
        'python-2.4.2-winsock2.patch',
        'python-2.4.2-setup.py-selectmodule.patch',
        'python-2.4.5-disable-pwd-mingw.patch',
        ]
    dependencies = [
        'db-devel',
        'expat-devel',
        'zlib-devel',
        'tools::python-2-6',
        ]
    config_cache_overrides = python.Python__mingw.config_cache_overrides + '''
ac_cv_have_chflags=no
ac_cv_have_lchflags=no
ac_cv_py_format_size_t=no
'''
    so_modules = Python_2_6.so_modules
    def patch (self):
        python.Python__mingw.patch (self)
        self.system ('cd %(srcdir)s && cp -pv PC/dl_nt.c Python/fileblocks.c')
    def generate_dll_a_and_la (self, libname, depend=''):
        target.AutoBuild.generate_dll_a_and_la (self, 'python2.6', depend)

class Python_2_6__tools (python.Python__tools):
    source = Python_2_6.source
    patches = []
    dependencies = ['autoconf', 'libtool']
    force_autoupdate = True
    make_flags = python.Python__tools.make_flags
    so_modules = Python_2_6.so_modules
    def patch (self):
        tools.AutoBuild.patch (self)
        # Stop python from reading ~/.inputrc
        self.apply_patch('python-2.6.4-readline.patch')
