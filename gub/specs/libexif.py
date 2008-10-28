from gub import targetbuild

class Libexif (targetbuild.AutoBuild):
# incompatible with gphoto?
#    source = mirrors.with_template (name='libexif', version="0.6.9", mirror=mirrors.sf)
# does not install
#    source = mirrors.with_template (name='libexif', version="0.6.14", mirror=mirrors.sf)
# too old for libgphoto-2.3.1
#    source = mirrors.with_template (name='libexif', version="0.6.12", mirror=mirrors.sf)
    source = 'http://surfnet.dl.sourceforge.net/sourceforge/libexif/libexif-0.6.15.tar.gz'
