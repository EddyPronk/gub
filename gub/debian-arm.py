import os
import re
#
from gub import cross
from gub import mirrors
from gub import gubb
from gub import linux
from gub import misc
from gub import targetpackage

class Debian_arm_runtime (gubb.BinarySpec, gubb.SdkBuildSpec):
    pass

def get_cross_packages (settings):
    from gub import debian
    return debian.get_cross_packages (settings)
    #return get_cross_packages_pre_eabi (settings)

def get_cross_packages_pre_eabi (settings):
    binutils_version = '2.16.1'
    gcc_version = '3.4.3' # only change
    guile_version = '1.6.7'
    kernel_version = '2.5.999-test7-bk-17'
    libc6_version = '2.3.2.ds1-22sarge4'
    python_version = '2.4.1'
    from gub import debian
    return debian._get_cross_packages (settings,
                                       binutils_version, gcc_version,
                                       guile_version,
                                       kernel_version, libc6_version,
                                       python_version)

def change_target_package (p):
    cross.change_target_package (p)
    return p
