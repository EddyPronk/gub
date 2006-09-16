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
    return debian.get_cross_packages_stable (settings)

def change_target_packages (packages):
    cross.change_target_packages (packages)
    cross.set_framework_ldpath ([p for p in packages.values ()
                                 if isinstance (p,
                                                targetpackage.TargetBuildSpec)])
    return packages
