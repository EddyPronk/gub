import os
import re
#
import cross
import download
import gub
import linux
import misc
import targetpackage

class Arm_runtime (gub.BinarySpec, gub.SdkBuildSpec):
    pass

def get_cross_packages (settings):
    import debian
    return debian.get_cross_packages (settings)

def change_target_package (p):
    cross.change_target_package (p)

    return p
