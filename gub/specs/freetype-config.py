import re
import os

from gub import build
from gub import misc
from gub import repository

class Freetype_config (build.SdkBuild):
    source = repository.Version (name='freetype-config', version='2.1.9')
    def stages (self):
        return [x for x in build.SdkBuild.stages (self)
                if x not in ['untar', 'patch']]
    def install (self):
        build.SdkBuild.install (self)
        ft_version = self.version ()
        prefix = '%(system_prefix)s'
        exec_prefix = '${prefix}'
        includedir = '%(prefix_dir)s/include'
        libdir = '%(prefix_dir)s/lib'
        enable_shared = 'yes'
        wl = '-Wl,'
        hardcode_libdir_flag_spec='${wl}--rpath ${wl}$libdir'
        LIBZ = '-lz'

        regexes = [('@%s@' % nm, self.expand ('%(' + nm + ')s', locals ()))
                   for nm in [ 'prefix', 'exec_prefix', 'includedir', 'libdir',
                               'enable_shared', 'wl', 'hardcode_libdir_flag_spec']]

        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        freetype_config = self.expand ('%(install_prefix)s%(cross_dir)s/bin/freetype-config')
        self.file_sub (regexes,
                       '%(sourcefiledir)s/freetype-config.in',
                       to_name=freetype_config,
                       use_re=False)
        self.chmod (freetype_config, 755)
        
class Freetype_config__cygwin (Freetype_config):
    source = repository.Version (name='freetype-config', version='2.3.4')
