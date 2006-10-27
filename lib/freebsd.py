import os
import re

import cross
import download
import gub
import misc
import targetpackage

class Binutils (cross.Binutils):
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        return (cross.Binutils.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))

class Gcc (cross.Gcc):
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        return (cross.Gcc.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))

class Freebsd_runtime (gub.BinarySpec, gub.SdkBuildSpec):
    def untar (self):
        gub.BinarySpec.untar (self)
    def patch (self):
        self.system ('rm -rf %(srcdir)s/usr/include/g++')

def _get_cross_packages (settings, libc_version):
    return (
        Freebsd_runtime (settings).with (version=libc_version,
                                         mirror=download.jantien),
        Binutils (settings).with (version='2.16.1', format='bz2', mirror=download.gnu),
        Gcc (settings).with (version='4.1.1', mirror=download.gcc_41,
                             format='bz2'),
        )

def get_cross_packages_41 (settings):
    return _get_cross_packages (settings, '4.10-2')

def get_cross_packages_61 (settings):
    return _get_cross_packages (settings, '6.1-RELEASE')

def get_cross_packages (settings):
    if settings.target_architecture == 'i686-freebsd4':
        return get_cross_packages_41 (settings)
    return get_cross_packages_61 (settings)

def change_target_package (package):
    cross.change_target_package (package)
    if isinstance (package, targetpackage.TargetBuildSpec):
        cross.set_framework_ldpath (package)

        
    
# FIXME: download from sane place.
def get_sdk():
    '''

#FIXME: how to get libc+kernel headers package contents on freebsd?
# * remove zlib.h, zconf.h or include libz and remove Zlib from src packages?
# * remove gmp.h, or include libgmp and remove Gmp from src packages?
# bumb version number by hand, sync with freebsd.py
freebsd-runtime:
	ssh xs4all.nl tar -C / --exclude=zlib.h --exclude=zconf.h --exclude=gmp.h -czf public_html/freebsd-runtime-4.10-2.tar.gz /usr/lib/{lib{c,c_r,m}{.a,.so{,.*}},crt{i,n,1}.o} /usr/include

    '''
