from gub import build

##class Mingw_pwd (build.SdkBuild): nicer as sdk, but triggers full rebuild
class Mingw_pwd (build.NullBuild):
    source = 'http://mingw/mingw-pwd-1.0.tar.gz'
    def stages (self):
        return ['untar', 'install', 'package', 'clean']
    def download (self):
        pass
    def untar (self):
        self.dump (r'''#! /bin/bash
options=$(echo -n "$@" | tr -d W | sed 's/-\( \|$\)/\1/')
builtin pwd $options
''',
                   '%(install_prefix)s%(cross_dir)s/bin/pwd', mode='w', permissions=0755)
