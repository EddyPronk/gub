import os
import re
import oslog
import distcc
import gub

from context import *

platforms = {
    'arm': 'arm-linux',
    'cygwin': 'i686-cygwin',
    'darwin-ppc': 'powerpc-apple-darwin7',
    'darwin-x86': 'i686-apple-darwin8',
    'debian': 'i686-linux',
    'freebsd-x86': 'i686-freebsd4',
    
    'freebsd4-x86': 'i686-freebsd4',
    'freebsd6-x86': 'i686-freebsd6',
    'linux-x86': 'i686-linux',
    'linux-64': 'x86_64-linux',
    'linux-ppc': 'powerpc-linux',
    'local': 'local',
    'mingw': 'i686-mingw32',
    'mipsel': 'mipsel-linux',
}

distros = ('arm', 'cygwin', 'debian', 'mipsel')
            
class Settings (Context):
    def __init__ (self, platform):
        Context.__init__ (self)
        self.platform = platform
        self.target_architecture = platforms[self.platform]
        self.build_source = False
        self.is_distro = platform in distros

        self.target_gcc_flags = '' 
        self.topdir = os.getcwd ()
        self.logdir = self.topdir + '/log'
        self.downloads = self.topdir + '/downloads'
        self.patchdir = self.topdir + '/patches'
        self.sourcefiledir = self.topdir + '/sourcefiles'
        self.specdir = self.topdir + '/specs'
        self.nsisdir = self.topdir + '/nsis'
        self.gtk_version = '2.8'

        self.tool_prefix = self.target_architecture + '-'
        self.targetdir = self.topdir + '/target/' + self.platform

        ## Patches are architecture dependent, 
        ## so to ensure reproducibility, we unpack for each
        ## architecture separately.
        self.allsrcdir = os.path.join (self.targetdir, 'src')
        
        self.allbuilddir = self.targetdir + '/build'
        self.statusdir = self.targetdir + '/status'

        ## Safe uploads, so that we can rm -rf target/*
        ## and still cheaply construct a (partly) system root
        ## from .gub packages.
        self.uploads = self.topdir + '/uploads'
        self.gub_uploads = self.uploads + '/' + self.platform

        ## FIXME
##        self.gub_cross_uploads = '%s/%s-cross' % (self.uploads, self.platform)

        self.distcc_hosts = ''
        # FIXME: rename to target_root?
        self.system_root = self.targetdir + '/system'
        self.cross_prefix = self.system_root + '/usr/cross'
        self.installdir = self.targetdir + '/install'
        self.local_prefix = self.topdir + '/target/local/system/usr'
        self.cross_distcc_bindir = self.topdir + '/target/cross-distcc/bin'
        self.native_distcc_bindir = self.topdir + '/target/native-distcc/bin'
        
	if self.target_architecture.startswith ('x86_64'):
	    self.package_arch = 'amd64'
            self.debian_branch = 'unstable'
	else:
            self.package_arch = re.sub ('-.*', '', self.target_architecture)
            self.package_arch = re.sub ('i[0-9]86', 'i386', self.package_arch)
            self.debian_branch = 'stable'
        
        self.keep_build = False
        self.use_tools = False
        self.build_autopackage = self.allbuilddir + '/autopackage'

        if not os.path.isdir ('log'):
            os.mkdir ('log')
            
        self.os_interface = oslog.Os_commands ('log/build-%s.log'
                                               % self.target_architecture)
        self.create_dirs ()
        self.build_architecture = self.os_interface.read_pipe ('gcc -dumpmachine',
                                                               silent=True)[:-1]

        try:
            self.cpu_count_str = '%d' % os.sysconf ('SC_NPROCESSORS_ONLN')
        except ValueError:
            self.cpu_count_str = '1'
            
    def verbose (self):
        try:
            return self.options.verbose
        except AttributeError:
            return False
    
    def create_dirs (self): 
        for a in (
            'downloads',
            'logdir',
            'gub_uploads',
#            'gub_cross_uploads',
            'specdir',
            'allsrcdir',
            'statusdir',
            'system_root',
            'cross_prefix',
            'targetdir',
            'local_prefix',
            'topdir',
            ):
            dir = self.__dict__[a]
            if os.path.isdir (dir):
                continue

            self.os_interface.system ('mkdir -p %s' % dir)


    def set_distcc_hosts (self, options):
        def hosts (xs):
            return reduce (lambda x,y: x+y,
                           [ h.split (',') for h in xs], [])
        
        self.cross_distcc_hosts = ' '.join (distcc.live_hosts (hosts (options.cross_distcc_hosts)))

        self.native_distcc_hosts = ' '.join (distcc.live_hosts (hosts (options.native_distcc_hosts), port=3634))



    def set_branches (self, bs):
        "set branches, takes a list of name=branch strings."

        self.branch_dict = {}
        for b in bs:
            (name, br) = tuple (b.split ('='))

            self.branch_dict[name] = br
            self.__dict__['%s_branch' % name]= br

            
def get_settings (platform):
    settings = Settings (platform)
    
    if platform not in platforms.keys ():
        raise 'unknown platform', platform
        
    if platform == 'darwin-ppc':
        settings.target_gcc_flags = '-D__ppc__'
    elif platform == 'mingw':
        settings.target_gcc_flags = '-mwindows -mms-bitfields'

    return settings


