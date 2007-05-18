from gub import gubb
from gub import mirrors
from gub import debian

class Linux_kernel_headers (gubb.BinarySpec, gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        self.with_template (
# FIXME: we do not mirror all 12 debian arch's,
#            version=debian.get_packages ()['linux-kernel-headers'].version (),
#           mirror=mirrors.lkh_deb,
            version='2.5.999-test7-bk-17',
            mirror=mirrors.lilypondorg_deb,
            strip_components=0,
            format='deb')
    def get_subpackage_names (self):
        return ['']
