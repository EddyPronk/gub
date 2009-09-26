from gub import target

class Popt (target.AutoBuild):
    source = 'http://rpm5.org/files/popt/popt-1.14.tar.gz'
    config_cache_overrides = target.AutoBuild.config_cache_overrides + '''
ac_cv_va_copy=${ac_cv_va_copy=C99}
'''

class Popt__freebsd__x86 (Popt):
    patches = ['popt-no-wchar-hack.patch']

class Popt__mingw (Popt):
    patches = ['popt-no-sys-ioctl.patch']
    configure_variables = (Popt.configure_variables
                           + ' CFLAGS="-Drandom=rand -Dsrandom=srand"')
