import os
#
from gub import misc
from gub import tools

class Rebase__tools (tools.MakeBuild):
    source = 'http://www.tishler.net/jason/software/rebase/rebase-2.4.2-1-src.tar.bz2'
    patches = ['rebase-2.4.2-1.patch']
    def get_build_dependencies (self):
        return ['mingw::cross/gcc']
    def patch (self):
        self.system ('dos2unix %(srcdir)s/imagehelper/*')
        tools.MakeBuild.patch (self)
    def makeflags (self):
        return misc.join_lines ('''
CC=i686-mingw32-gcc
CXX=i686-mingw32-g++
AR=i686-mingw32-ar
LIBRESTRICT_ALLOW=%(targetdir)s
PREFIX=%(system_prefix)s
''')
    # C&P from nsis.  Should move to mingw.
    def add_mingw_env (self):
        # Do not use 'root', 'usr', 'cross', rather use from settings,
        # that enables changing system root, prefix, etc.
        mingw_dir = (self.settings.alltargetdir + '/mingw'
                     + self.settings.root_dir)
        mingw_bin = (mingw_dir
                     + self.settings.prefix_dir
                     + self.settings.cross_dir
                     + '/bin')
        tools_dir = (self.settings.alltargetdir + '/tools'
                     + self.settings.root_dir)
        tools_bin = (tools_dir
                     + self.settings.prefix_dir
                     + '/bin')
        return {'PATH': mingw_bin + ':' + tools_bin + ':' + os.environ['PATH'] }
    def build_environment (self):
        return self.add_mingw_env ()
    def compile (self):
        self.system ('cd %(builddir)s && %(compile_command)s',
                     self.build_environment ())
    def install (self):
        self.system ('cd %(builddir)s && %(install_command)s ',
                     self.build_environment ())
