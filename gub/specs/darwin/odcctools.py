import os
#
from gub import cross

class Odcctools (cross.AutoBuild):
    source = ('svn:http://iphone-dev.googlecode.com/svn&branch=trunk'
              '&module=odcctools'
              '&revision=278')
    patches = ['odcctools-r211-word.patch']
    def __init__ (self, settings, source):
        cross.AutoBuild.__init__ (self, settings, source)
        if 'x86_64-linux' in self.settings.build_architecture:
            # odcctools does not build with 64 bit compiler
            cross.change_target_package_x86 (self, self.add_linux_x86_env ())
    def add_linux_x86_env (self):
        # Do not use 'root', 'usr', 'cross', rather use from settings,
        # that enables changing system root, prefix, etc.
        linux_x86_dir = (self.settings.alltargetdir + '/linux-x86'
                         + self.settings.root_dir)
        linux_x86_bin = (linux_x86_dir
                         + self.settings.prefix_dir
                         + self.settings.cross_dir
                         + '/bin')
        linux_x86_i686_linux_bin = (linux_x86_dir
                                    + self.settings.prefix_dir
                                    + self.settings.cross_dir
                                    + '/i686-linux'
                                    + '/bin')
        tools_dir = (self.settings.alltargetdir + '/tools'
                     + self.settings.root_dir)
        tools_bin = (tools_dir
                     + self.settings.prefix_dir
                     + '/bin')
        return {'PATH': linux_x86_bin + ':' + linux_x86_i686_linux_bin + ':' + tools_bin + ':' + os.environ['PATH'] }
    def get_build_dependencies (self):
        lst = ['darwin-sdk']
        if 'x86_64-linux' in self.settings.build_architecture:
            lst += ['linux-x86::glibc']
        return lst
    def configure (self):
        cross.AutoBuild.configure (self)
        ## remove LD64 support.
        self.file_sub ([('ld64','')], self.builddir () + '/Makefile')
    def build_environment (self):
        return self.add_linux_x86_env ()
    def compile (self):
        self.system ('cd %(builddir)s && %(compile_command)s',
                     self.build_environment ())
    def install (self):
        self.system ('cd %(builddir)s && %(install_command)s ',
                     self.build_environment ())
