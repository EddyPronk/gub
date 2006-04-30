import os
import re

import cross
import download
import framework
import gub
import misc
import targetpackage

class Binutils (cross.Binutils):
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        return (cross.Binutils.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))

class Gcc (cross.Gcc):
    def configure_command (self):
        # Add --program-prefix, otherwise we get
        # i686-freebsd-FOO iso i686-freebsd4-FOO.
        return (cross.Gcc.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(tool_prefix)s
'''))

class Freebsd_runtime (gub.Binary_package, gub.Sdk_package):
    def patch (self):
        self.system ('rm -rf %(srcdir)s/root/usr/include/g++')

def get_cross_packages (settings):
    return (
        Freebsd_runtime (settings).with (version='4.10-2', mirror=download.jantien),
        Binutils (settings).with (version='2.16.1', format='bz2'),
        Gcc (settings).with (version='4.1.0', mirror=download.gcc_41,
                  format='bz2', depends=['binutils']),
        )


def change_target_packages (packages):
    cross.change_target_packages (packages)
    cross.set_framework_ldpath ([p for p in packages.values ()
                  if isinstance (p, targetpackage.Target_package)])
