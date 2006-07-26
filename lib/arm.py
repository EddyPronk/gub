import os
import re

import cross
import download
import gub
import linux
import misc
import targetpackage

class Arm_runtime (gub.BinarySpec, gub.SdkBuildSpec):
    pass

def get_cross_packages (settings):
    return (
        linux.Libc6 (settings).with (version='2.2.5-11.8',
                                     mirror=download.glibc_deb,
                                     format='deb'),
        linux.Libc6_dev (settings).with (version='2.2.5-11.8',
                                         mirror=download.glibc_deb,
                                         format='deb'),
        linux.Linux_kernel_headers (settings).with (version='2.6.13+0rc3-2',
                                                    mirror=download.lkh_deb,
                                                    format='deb'),
        cross.Binutils (settings).with (version='2.16.1', format='bz2'),
        cross.Gcc (settings).with (version='4.1.1', mirror=download.gcc_41,
                                   format='bz2'),
        )


def change_target_packages (packages):
    cross.change_target_packages (packages)
    cross.set_framework_ldpath ([p for p in packages.values ()
                                 if isinstance (p,
                                                targetpackage.TargetBuildSpec)])
    return packages
