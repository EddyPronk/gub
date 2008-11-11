from gub import build

## change to sdk package

## FIXME: having Python be an SDK package, will make cross.py add Python
## as a build dependency to all cross and other packs.
## *BUT* only *IF* Python is also built.  Which means that:
##    bin/gub darwin-ppc::odcctools [PACKAGE]...
##    bin/gub darwin-ppc::odcctools darwin-ppc::python [PACKAGE]...
## will set different build dependencies for all packages, and
## each will trigger a rebuild, depending upon the availability of Python
## on the command line [or as a build dependency of any PACKAGE].

## Please, un-make this an SDK package?  Adding python as a static
## cross dependency for now...

# this is only a python-config placeholder
class Python__darwin (build.SdkBuild):
    source = 'url://host/python-2.3.tar.gz'
    def srcdir (self):
        return '%(allsrcdir)s/python-darwin'
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
