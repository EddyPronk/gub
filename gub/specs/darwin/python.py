from gub import build
from gub import repository

## change to sdk package
class Python (build.SdkBuild):
    source = repository.Version (name='python', version='2.3')

    def srcdir (self):
        return '%(allsrcdir)s/python-darwin'
    def package (self):
        build.AutoBuild.package (self)
    def install (self):
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        self.dump ('''#! /bin/sh
if test "$1" = "--cflags"; then
  echo "-I%(system_root)s/System/Library/Frameworks/Python.framework/Versions/%(version)s/include/python%(version)s"
fi
if test "$1" = "--ldflags"; then
  echo ""
fi
''', '%(install_prefix)s%(cross_dir)s/bin/python-config')
        self.system ('chmod +x %(install_prefix)s%(cross_dir)s/bin/python-config')
