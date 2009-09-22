import os
#
from gub import cross
from gub import misc

# FIMXE: weird, we should be cross/odcctools
class Odcctools (cross.AutoBuild): #skews dependencies:, build.SdkBuild):
    source = ('svn:http://iphone-dev.googlecode.com/svn&module=trunk'
              '&branch=odcctools'
              '&revision=278')
    # let's use cached tarball
    source = 'http://lilypond.org/download/gub-sources/odcctools-iphone-dev-278.tar.gz'
    patches = ['odcctools-r211-word.patch',
               'odcctools-config-Wno-long-double.patch']
    def __init__ (self, settings, source):
        cross.AutoBuild.__init__ (self, settings, source)
        if 'x86_64-linux' in self.settings.build_architecture:
            # odcctools does not build with 64 bit compiler
            cross.change_target_package_x86 (self, self.add_linux_x86_env ())
    def _get_build_dependencies (self):
        lst = ['darwin-sdk', 'tools::flex']
        if 'x86_64-linux' in self.settings.build_architecture:
            lst += ['linux-x86::glibc']
        return lst
    def stages (self):
        return misc.list_insert_before (cross.AutoBuild.stages (self),
                                        'compile', ['patch_configure'])
    def add_linux_x86_env (self):
        # Do not use 'root', 'usr', 'cross', rather use from settings,
        # that enables changing system root, prefix, etc.
        linux_x86_dir = (self.settings.alltargetdir + '/linux-x86'
                         + self.settings.root_dir)
        linux_x86_bin = (linux_x86_dir
                         + self.settings.prefix_dir
                         + self.settings.cross_dir
                         + '/bin')
        linux_x86_i686_linux_bin = (linux_x86_dir
                                    + self.settings.prefix_dir
                                    + self.settings.cross_dir
                                    + '/i686-linux'
                                    + '/bin')
        tools_dir = (self.settings.alltargetdir + '/tools'
                     + self.settings.root_dir)
        tools_bin = (tools_dir
                     + self.settings.prefix_dir
                     + '/bin')
        return {'PATH': linux_x86_bin + ':' + linux_x86_i686_linux_bin + ':' + tools_bin + ':' + os.environ['PATH'] }
    def patch_configure (self):
        ## remove LD64 support.
        self.file_sub ([('ld64','')], self.builddir () + '/Makefile')
    def build_environment (self):
        return self.add_linux_x86_env ()
    def configure_command (self):
        if (self.settings.build_bits == '32'
            and self.settings.build_hardware_bits == '64'):
            return (cross.AutoBuild.configure_command (self)
                    + ' CFLAGS=-D_FORTIFY_SOURCE=0')
        return cross.AutoBuild.configure_command (self)
    def install_librestrict_stat_helpers (self):
        # librestrict stats PATH to find gnm and gstrip
        self.system ('''
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)sas %(toolchain_prefix)sgas
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)snm %(toolchain_prefix)sgnm
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)sstrip %(toolchain_prefix)sgstrip
mkdir -p %(install_prefix)s%(cross_dir)s/%(target_architecture)s/bin
cd %(install_prefix)s%(cross_dir)s/bin && for i in ar as ld nm ranlib strip; do ln %(toolchain_prefix)s$i ../%(target_architecture)s/bin/$i; done
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)sas ../%(target_architecture)s/bin/gas
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)snm ../%(target_architecture)s/bin/gnm
cd %(install_prefix)s%(cross_dir)s/bin && ln %(toolchain_prefix)sstrip ../%(target_architecture)s/bin/gstrip
''')
    def install (self):
        cross.AutoBuild.install (self)
        self.install_librestrict_stat_helpers ()
