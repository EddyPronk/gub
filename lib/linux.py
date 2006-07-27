import glob
import os
import re

import cross
import download
import gub
import targetpackage

class Libc6 (gub.BinarySpec, gub.SdkBuildSpec):
    def patch (self):
        self.system ('cd %(srcdir)s && rm -rf usr/sbin/ sbin/ bin/ usr/bin')

class Libc6_dev (gub.BinarySpec, gub.SdkBuildSpec):
    def untar (self):
        gub.BinarySpec.untar (self)
        # Ugh, rewire absolute names and symlinks.
        # Better to create relative ones?

        # FIXME: this rewiring breaks ld badly, it says
        #     i686-linux-ld: cannot find /home/janneke/bzr/gub/target/i686-linux/system/lib/libc.so.6 inside /home/janneke/bzr/gub/target/i686-linux/system/
        # although that file exists.  Possibly rewiring is not necessary,
        # but we can only check on non-linux platform.
        # self.file_sub ([(' /', ' %(system_root)s/')],
        #               '%(srcdir)s/root/usr/lib/libc.so')

        for i in glob.glob (self.expand ('%(srcdir)s/root/usr/lib/lib*.so')):
            if os.path.islink (i):
                s = os.readlink (i)
                if s.startswith ('/'):
                    os.remove (i)
                    os.symlink (self.settings.system_root
                          + s, i)
        for i in ('pthread.h', 'bits/sigthread.h'):
            self.file_sub ([('__thread', '___thread')],
                           '%(srcdir)s/root/usr/include/%(i)s',
                           env=locals ())
            
        self.system ('rm -rf  %(srcdir)s/root/usr/include/asm/  %(srcdir)s/root/usr/include/linux ')
            
class Linux_kernel_headers (gub.BinarySpec, gub.SdkBuildSpec):
    def get_subpackage_names (self):
        return ['']

class Libdbi0_dev (gub.BinarySpec, gub.SdkBuildSpec):
    pass

class Gcc (cross.Gcc):
    ## TODO: should detect whether libc supports TLS 
    def configure_command (self):
        return cross.Gcc.configure_command (self) + ' --disable-tls '

def get_cross_packages (settings):
    packages = [
        Libc6 (settings).with (version='2.2.5-11.8',
                               mirror=download.glibc_deb, format='deb'),
        Libc6_dev (settings).with (version='2.2.5-11.8',
                                   mirror=download.glibc_deb, format='deb'),
        Linux_kernel_headers (settings).with (version='2.6.13+0rc3-2.1',
                                              mirror=download.lkh_deb, format='deb'),
        cross.Binutils (settings).with (version='2.16.1', format='bz2'),
        Gcc (settings).with (version='4.1.1',
                             mirror=download.gcc, format='bz2'),
        ]
    return packages

class Guile_config (gub.SdkBuildSpec):
    def __init__ (self, settings):
        gub.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False

    def untar (self):
        pass

    def install (self):
        gub.SdkBuildSpec.install (self)
        self.system ('mkdir -p %(cross_prefix)s/usr/bin')
        
        version = self.version ()
        self.dump ('''\
#!/bin/sh
[ "$1" == "--version" ] && echo "%(target_architecture)s-guile-config - Guile version %(version)s"
prefix=$(dirname $(dirname $0))
[ "$1" == "compile" ] && echo "-I$prefix/include"
#[ "$1" == "link" ] && echo "-L$prefix/lib -lguile -lgmp"
# KUCH, debian specific, and [mipsel] reading .la is broken?
[ "$1" == "link" ] && echo "-L$prefix/lib -lguile -lguile-ltdl  -ldl -lcrypt -lm"
exit 0
''',
             '%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config')
        os.chmod ('%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config'
                  % self.get_substitution_dict (), 0755)

class Python_config (gub.SdkBuildSpec):
    def __init__ (self, settings):
        gub.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False

    def untar (self):
        pass

    def install (self):
        gub.SdkBuildSpec.install (self)
        self.system ('mkdir -p %(cross_prefix)s/usr/bin')
        cfg = open (self.expand ('%(sourcefiledir)s/python-config.py.in')).read ()
        cfg = re.sub ('@PYTHON_VERSION@', self.expand ('%(version)s'), cfg)
        cfg = re.sub ('@PREFIX@', self.expand ('%(system_root)s/usr/'), cfg)
        import sys
        cfg = re.sub ('@PYTHON_FOR_BUILD@', sys.executable, cfg)
        self.dump (cfg, '%(install_root)s/usr/cross/bin/python-config',
                   expand_string=False)
        self.system ('chmod +x %(install_root)s/usr/cross/bin/python-config')

def change_target_packages (packages):
    cross.change_target_packages (packages)
    for p in packages.values ():
        if isinstance (p, targetpackage.TargetBuildSpec):
            gub.change_target_dict (p,
                        {'LD': '%(target_architecture)s-ld --as-needed ',
                        })

            gub.append_target_dict (p,
                        { 'LDFLAGS': ' -Wl,--as-needed ' })

    cross.set_framework_ldpath ([p for p in packages.values ()
                                 if isinstance (p, targetpackage.TargetBuildSpec)])
