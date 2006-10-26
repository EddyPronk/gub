import os
import re
#
import cross
import gub
import targetpackage

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
	#FIXME: c&p guile.py
        self.dump ('''\
#! /bin/sh
test "$1" = "--version" && echo "%(target_architecture)s-guile-config - Guile version %(version)s"
prefix=$(dirname $(dirname $0))
test "$1" = "compile" && echo "-I$prefix/include"
#test "$1" = "link" && echo "-L$prefix/lib -lguile -lgmp"
# KUCH, debian specific, and [mipsel] reading .la is broken?
test "$1" = "link" && echo "-L$prefix/lib -lguile -lguile-ltdl  -ldl -lcrypt -lm"
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

def change_target_package (package):
    cross.change_target_package (package)
    if isinstance (package, targetpackage.TargetBuildSpec):
        gub.change_target_dict (package,
                        {'LD': '%(target_architecture)s-ld --as-needed ',
                        })

        gub.append_target_dict (package,
                                { 'LDFLAGS': ' -Wl,--as-needed ' })

    if isinstance (package, targetpackage.TargetBuildSpec):
       cross.set_framework_ldpath (package)
    return package

def get_cross_packages (settings):
    import debian
    return debian.get_cross_packages (settings)

