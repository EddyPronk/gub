from gub import gubb

class Freetype_config (gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False
        self.with_template (version='2.1.9')
    def untar (self):
        pass
    def install (self):
        gubb.SdkBuildSpec.install (self)
        self.system ('mkdir -p %(cross_prefix)s/usr/bin')
        
        ft_version = self.version ()
        prefix = '%(system_root)s/usr'
        exec_prefix = '${prefix}'
        includedir = '/usr/include'
        libdir = '/usr/lib'
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
        os.chmod (file, 0755)

class Freetype_config__cygwin (Freetype_config):
    def __init__ (self, settings):
        Freetype_config.__init__ (self, settings)
        self.with_template (version='2.3.4')
        
