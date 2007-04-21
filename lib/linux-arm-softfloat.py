import cross
import gcc
import glibc
import linux


'''
Configured with: /work/GNU/CodeSourcery/src/gcc-3.4.0/configure 
--target=arm-linux 
--host=i686-host_pc-linux-gnu 
--prefix=/usr/local/arm/gnu/release-3.4.0-vfp 
--with-headers=/usr/local/arm/gnu/release-3.4.0-vfp/arm-linux/include 
--with-local-prefix=/usr/local/arm/gnu/release-3.4.0-vfp/arm-linux 
--disable-nls 
--enable-threads=posix 
--enable-symvers=gnu 
--enable-__cxa_atexit 
--enable-languages=c,c++ 
--enable-shared 
--enable-c99 
--enable-clocale=gnu 
--enable-long-long
'''

class Gcc (gcc.Gcc):
    def configure_command (self):
        return (gcc.Gcc.configure_command (self)
                + misc.join_lines ('''
--with-float=soft
'''))

class Gcc_core (gcc.Gcc_core):
    def configure_command (self):
        return (gcc.Gcc_core.configure_command (self)
                + misc.join_lines ('''
--with-float=soft
'''))

class Glibc (glibc.Glibc):
    def configure_command (self):
        return (glibc.Glibc.configure_command (self)
                + misc.join_lines ('''
--without-fp
'''))

class Glibc_core (glibc.Glibc_core):
    def configure_command (self):
        return (glibc.Glibc_core.configure_command (self)
                + misc.join_lines ('''
--without-fp
'''))

#FIXME, c&p linux.py
import download
import misc
def _get_cross_packages (settings,
                         linux_version, binutils_version, gcc_version,
                         glibc_version, guile_version, python_version):
    configs = []
    if not settings.platform.startswith ('linux'):
        configs = [
            linux.Guile_config (settings).with (version=guile_version),
            linux.Python_config (settings).with (version=python_version),
            ]

    import linux_headers
    import debian
    import binutils
    import gcc
    import glibc
    headers = linux_headers.Linux_headers (settings)\
        .with_tarball (mirror=download.linux_2_6,
                       version=linux_version,
                       format='bz2')
    if settings.package_arch == 'arm':
        headers = debian.Linux_kernel_headers (settings)\
            .with (version=linux_version,
                   strip_components=0,
                   mirror=download.lilypondorg_deb,
                   format='deb')
    return [
        headers,
        binutils.Binutils (settings).with (version=binutils_version,
                                           format='bz2', mirror=download.gnu),
        Gcc_core (settings).with (version=gcc_version,
                                  mirror=(download.gcc
                                          % {'name': 'gcc',
                                             'ball_version': gcc_version,
                                             'format': 'bz2',}),
                                  format='bz2'),
        Glibc_core (settings).with (version=glibc_version,
                                    #mirror=(download.glibc
                                    mirror=(download.glibc_2_3_snapshots
                                            % {'name': 'glibc',
                                               'ball_version': glibc_version,
                                               'format': 'bz2',}),
                                    format='bz2'),
        Gcc (settings).with (version=gcc_version,
                                 mirror=download.gcc, format='bz2'),
        Glibc (settings).with (version=glibc_version,
                               #mirror=download.gnu,
                               mirror=download.glibc_2_3_snapshots,
                               format='bz2'),
        ] + configs



def get_cross_packages (settings):
    return get_cross_packages_pre_eabi (settings)

def get_cross_packages_pre_eabi (settings):
    #linux_version = '2.5.75'
    linux_version = '2.5.999-test7-bk-17'
    binutils_version = '2.16.1'
    gcc_version = '3.4.5'
    #glibc_version = '2.3.6'
    glibc_version = '20070416'
    guile_version = '1.6.7'
    python_version = '2.4.1'
    return _get_cross_packages (settings,
                                linux_version, binutils_version,
                                gcc_version, glibc_version,
                                guile_version, python_version)

def change_target_package (p):
    cross.change_target_package (p)
    return p
