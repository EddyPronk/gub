from gub import gubb
from gub import mirrors

class Freebsd_runtime (gubb.BinarySpec, gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        version = '4.10-2'
        if 0 and settings.target_architecture == 'i686-freebsd6':
            version = '6.1-RELEASE'
        if settings.target_architecture.startswith ('x86_64-freebsd'):
            version = '6.2-1.amd64'
        self.with_template (version=version, strip_components=0, mirror=mirrors.lilypondorg)
    def untar (self):
        gubb.BinarySpec.untar (self)
    def patch (self):
        self.system ('rm -rf %(srcdir)s/usr/include/g++')
