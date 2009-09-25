import os
import re
#
from gub import tools
from gub import loggedos

class Binutils__tools (tools.AutoBuild):
    source = 'http://ftp.gnu.org/pub/gnu/binutils/binutils-2.19.1.tar.gz'
    dependencies = ['system::gcc']
        # binutils' makefile uses:
        #     MULTIOSDIR = `$(CC) $(LIBCFLAGS) -print-multi-os-directory`
        # which differs on each system.  Setting it avoids inconsistencies.
    make_flags = 'MULTIOSDIR=../../lib'
    def install (self):
        tools.AutoBuild.install (self)
        install_librestrict_stat_helpers (self)
        remove_fedora9_untwanted_but_mysteriously_built_libiberies (self)

def remove_fedora9_untwanted_but_mysteriously_built_libiberies (self):
    self.system ('rm -f %(install_prefix)s/lib/libiberty.a')
    self.system ('rm -f %(install_prefix)s/lib64/libiberty.a')

def add_g_file_names (logger, file_name):
    dir_name = os.path.dirname (file_name)
    base_name = os.path.basename (file_name)
    gnu_base_name = 'g' + base_name
    if '-' in base_name:
        gnu_base_name = re.sub ('-([^/g][^/-]*)$', r'-g\1', base_name)
    gnu_file_name = os.path.join (dir_name, gnu_base_name)
    loggedos.link (logger, file_name, gnu_file_name)

def install_librestrict_stat_helpers (self):
    # LIBRESTRICT stats PATH to find gnm and gstrip
    for d in [
        '%(install_prefix)s/bin',
        '%(install_prefix)s%(cross_dir)s/bin',
        '%(install_prefix)s%(cross_dir)s/%(target_architecture)s/bin',
        ]:
        self.map_find_files (add_g_file_names, d, '(^|.*/)([^/g][^-/]*|.*-[^/g][^-/]*)$')
