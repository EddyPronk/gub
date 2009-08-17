from gub import build

import os
if 'BOOTSTRAP' in os.environ.keys (): from gub import target as tools

class Gub_utils__tools (build.SdkBuild):
    source = 'url://host/gub-utils-1.0.tar.gz'
    def install (self):
        build.SdkBuild.install (self)
        self.system ('mkdir -p %(srcdir)s/%(prefix_dir)s/bin')
        self.dump ('''#! /bin/bash
echo gub-build
''',
                  '%(srcdir)s/%(prefix_dir)s/bin/hostname')
