from gub import gubb

## change to sdk package
class Python (gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.NullBuildSpec.__init__ (self, settings)
        self.version = (lambda: '2.3')
        self.vc_branch = ''
        self.format = ''
        self.has_source = False

    def srcdir (self):
        return '%(allsrcdir)s/python-darwin'

    def package (self):
        gubb.BuildSpec.package (self)
        
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
