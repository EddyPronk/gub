from gub import target

class Popt (target.AutoBuild):
    source = 'http://rpm5.org/files/popt/popt-1.14.tar.gz'
    def config_cache_overrides (self, string):
        return (string
                + '\nac_cv_va_copy=${ac_cv_va_copy=C99}\n')

class Popt__mingw (Popt):
    patches = ['popt-no-sys-ioctl.patch']
    def configure_command (self):
        return (Popt.configure_command (self)
                + ' CFLAGS="-Drandom=rand -Dsrandom=srand"')
