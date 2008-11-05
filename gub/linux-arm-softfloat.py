from gub import build
from gub import cross

code_sourcery = 'http://www.codesourcery.com/public/gnu_toolchain/%(name)s/arm-%(ball_version)s-%(name)s.src.tar.%(format)s'

class Arm_none_elf (build.BinaryBuild, build.SdkBuild):
    def install (self):
        self.system ('''
mv %(srcdir)s/*gz %(downloads)s
mkdir -p %(install_root)s
''')

def get_cross_build_dependencies (settings):
    return ['linux-headers', 'glibc']

def change_target_package (p):
    cross.change_target_package (p)
    return p
