from gub import build

class Freetype_config (build.SdkBuild):
    def __init__ (self, settings, source):
        build.SdkBuild.__init__ (self, settings, source)
        self.has_source = False
    source = mirrors.with_template (name='freetype-config', version='2.1.9')
    def untar (self):
        pass
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
        s = open (self.expand ('%(sourcefiledir)s/freetype-config.in')).read ()
        s = re.sub (r'@(\w+?)@', r'%(\1)s', s)
        s = s % locals ()
        file = self.expand ('%(install_prefix)s/cross/bin/freetype-config')
        self.dump (s, file)
        self.chmod (file, 0755)

class Freetype_config__cygwin (Freetype_config):
    def __init__ (self, settings, source):
        Freetype_config.__init__ (self, settings, source)
    source = mirrors.with_template (name='freetype-config', version='2.3.4')
        
