from gub import gubb

code_sourcery = 'http://www.codesourcery.com/public/gnu_toolchain/%(name)s/arm-%(ball_version)s-%(name)s.src.tar.%(format)s'

class Arm_none_elf (gubb.BinarySpec, gubb.SdkBuildSpec):
    def install (self):
        self.system ('''
mv %(srcdir)s/*gz %(downloads)s
mkdir -p %(install_root)s
''')

def get_cross_packages (settings):
    # obsolete
    return []

def get_cross_build_dependencies (settings):
    return ['linux-headers', 'glibc']

def change_target_package (p):
    from gub import cross
    cross.change_target_package (p)
    return p
