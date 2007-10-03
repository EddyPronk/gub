from gub import build
from gub import misc
from gub import repository

class Freetype_config (build.SdkBuild):
    source = repository.Version (name='freetype-config', version='2.1.9')
    def stages (self):
        return misc.list_remove (build.SdkBuild.stages (self),
                       ['download', 'untar', 'patch'])
    def install (self):
        build.SdkBuild.install (self)
        self.system ('mkdir -p %(cross_prefix)s/usr/bin')
        
        ft_version = self.version ()
        prefix = '%(system_prefix)s'
        exec_prefix = '${prefix}'
        includedir = '%(prefix_dir)s/include'
        libdir = '%(prefix_dir)s/lib'
        enable_shared = 'yes'
        wl = '-Wl,'
        hardcode_libdir_flag_spec='${wl}--rpath ${wl}$libdir'
        LIBZ = '-lz'

        import re
        import os
        s = self.read_file ('%(sourcefiledir)s/freetype-config.in')
        s = re.sub (r'@(\w+?)@', r'%(\1)s', s)
        s = s % locals ()
        self.dump (s, '%(install_prefix)s/cross/bin/freetype-config',
                   env=locals (),
                   permissions=0755)

class Freetype_config__cygwin (Freetype_config):
    source = repository.Version (name='freetype-config', version='2.3.4')
