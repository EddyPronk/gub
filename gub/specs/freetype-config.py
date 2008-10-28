from gub import build

class Freetype_config (build.SdkBuild):
    source = 'url://host/freetype-config-2.1.9.tar.gz'
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
                               'enable_shared', 'wl', 'hardcode_libdir_flag_spec', 'LIBZ']]

        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        freetype_config = self.expand ('%(install_prefix)s%(cross_dir)s/bin/freetype-config')
        self.file_sub (regexes,
                       '%(sourcefiledir)s/freetype-config.in',
                       to_name=freetype_config,
                       use_re=False)
        self.system ('find %(install_prefix)s')
        self.chmod (freetype_config, 0755)
        
class Freetype_config__cygwin (Freetype_config):
    source = 'url://host/freetype-config-2.3.4.tar.gz'
