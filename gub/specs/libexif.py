from gub import targetbuild
from gub import mirrors

class Libexif (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
# incompatible with gphoto?
#    source = mirrors.with_template (name='libexif', version="0.6.9", mirror=mirrors.sf)
# does not install
#    source = mirrors.with_template (name='libexif', version="0.6.14", mirror=mirrors.sf)
# too old for libgphoto-2.3.1
#    source = mirrors.with_template (name='libexif', version="0.6.12", mirror=mirrors.sf)
    source = mirrors.with_template (name='libexif', version="0.6.15", mirror=mirrors.sf)
