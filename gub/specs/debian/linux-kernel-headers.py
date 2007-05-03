from gub import gubb
from gub import mirrors
from gub import debian

class Linux_kernel_headers (gubb.BinarySpec, gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        self.with (version=debian.get_packages ()['linux-kernel-headers'].version (),
                   strip_components=0,
                   mirror=mirrors.lkh_deb,
# FIXME: we do not mirror all 12 debian arch's,
#                   mirror=mirrors.lilypondorg_deb,
                   format='deb')
    def get_subpackage_names (self):
        return ['']
