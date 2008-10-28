from gub import build

## change to sdk package
class Python (build.SdkBuild):
    source = 'url://host/python-2.3.tar.gz'
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
