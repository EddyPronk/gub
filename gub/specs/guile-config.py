from gub import build

class Guile_config (build.SdkBuild):
    def __init__ (self, settings, source):
        build.SdkBuild.__init__ (self, settings, source)
        self.has_source = False
    source = mirrors.with_template (name='guile-config', version='1.8.0')

    def untar (self):
        pass

    def install (self):
        build.SdkBuild.install (self)
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
        self.chmod ('%(install_prefix)s/cross/bin/%(target_architecture)s-guile-config', 0755)
