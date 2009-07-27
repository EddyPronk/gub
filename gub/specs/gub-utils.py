from gub import build

class Gub_utils (build.SdkBuild):
    source = 'url://host/gub-utils-1.0.tar.gz'
    def install (self):
        build.SdkBuild.install (self)
        self.system ('mkdir -p %(srcdir)s/%(prefix_dir)s/bin')
        self.dump ('''#! /bin/bash
echo gub-build
''',
                  '%(srcdir)s/%(prefix_dir)s/bin/hostname')
