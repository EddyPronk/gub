from gub import gubb

class Guile_config (gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False
        self.with_template (version='1.8.0')

    def untar (self):
        pass

    def install (self):
        gubb.SdkBuildSpec.install (self)
        self.system ('mkdir -p %(cross_prefix)s%(prefix_dir)s/bin')
        
        import os
        version = self.version ()
	#FIXME: c&p guile.py
        self.dump ('''\
#! /bin/sh
test "$1" = "--version" && echo "%(target_architecture)s-guile-config - Guile version %(version)s"
#prefix=$(dirname $(dirname $0))
prefix=%(system_prefix)s
test "$1" = "compile" && echo "-I$prefix/include"
#test "$1" = "link" && echo "-L$prefix/lib -lguile -lgmp"
# KUCH, debian specific, and [mipsel] reading .la is broken?
test "$1" = "link" && echo "-L$prefix/lib -lguile -lguile-ltdl  -ldl -lcrypt -lm"
exit 0
''',
             '%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config')
        os.chmod ('%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config'
                  % self.get_substitution_dict (), 0755)
