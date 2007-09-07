import os
import re
from gub import oslog
from gub import distcc
from gub import gubb
from gub import context

platforms = {
    'debian': 'i686-linux',
    'debian-arm': 'arm-linux',
    'debian-mipsel': 'mipsel-linux',
    'debian-x86': 'i686-linux',
    'cygwin': 'i686-cygwin',
    'darwin-ppc': 'powerpc-apple-darwin7',
    'darwin-x86': 'i686-apple-darwin8',

    'freebsd4-x86': 'i686-freebsd4',
    'freebsd6-x86': 'i686-freebsd6',

    'freebsd-x86': 'i686-freebsd4',
    'freebsd-64': 'x86_64-freebsd6',

    'linux-arm-softfloat': 'armv5te-softfloat-linux',
    'linux-arm-vfp': 'arm-linux',
    'linux-x86': 'i686-linux',
    'linux-64': 'x86_64-linux',
    'linux-ppc': 'powerpc-linux',
    'local': 'local',
    'mingw': 'i686-mingw32',
}

distros = ('cygwin')
            
class Settings (context.Context):
    def __init__ (self, options):
        context.Context.__init__ (self)
        self.platform = options.platform

        if self.platform not in platforms.keys ():
            raise 'unknown platform', self.platform

        # config dirs

        # gubdir is top of `installed' gub repository
        self.gubdir = os.getcwd ()

        # workdir is top of writable build stuff
        self.workdir = os.getcwd ()
        
        # gubdir based: fixed repository layout
        self.patchdir = self.gubdir + '/patches'
        self.sourcefiledir = self.gubdir + '/sourcefiles'
        self.specdir = self.gubdir + '/gub/specs'
        self.nsisdir = self.gubdir + '/nsis'

        # workdir based; may be changed
        self.logdir = self.workdir + '/log'
        self.downloads = self.workdir + '/downloads'
        self.alltargetdir = self.workdir + '/target'
        self.targetdir = self.alltargetdir + self.platform

        self.system_root = self.targetdir + '/root'
        ## Patches are architecture dependent, 
        ## so to ensure reproducibility, we unpack for each
        ## architecture separately.
        self.allsrcdir = self.targetdir, '/src'
        self.allbuilddir = self.targetdir + '/build'
        self.statusdir = self.targetdir + '/status'

        self.uploads = self.workdir + '/uploads'
        self.packages = self.workdir + '/packages/' + self.platform
        self.platform_uploads = self.uploads + '/' + self.platform

        # FIXME: rename to cross_root?
        self.cross_prefix = self.system_root + '/usr/cross'
        self.installdir = self.targetdir + '/install'
        self.local_prefix = self.alltargetdir + '/local/usr'
        self.cross_distcc_bindir = self.alltargetdir + '/cross-distcc/bin'
        self.native_distcc_bindir = self.alltargetdir + '/native-distcc/bin'

        self.cross_packages = self.packages + '/cross'
        self.cross_allsrcdir = self.allsrcdir + '/cross'
        self.cross_statusdir = self.statusdir + '/cross'

        self.core_prefix = self.system_root + '/usr/cross/core'
        # end config dirs



        self.target_gcc_flags = '' 
        if self.platform == 'darwin-ppc':
            self.target_gcc_flags = '-D__ppc__'
        elif self.platform == 'mingw':
            self.target_gcc_flags = '-mwindows -mms-bitfields'

        self.set_branches (options.branches)
        self.options = options ##ugh
        self.verbose = self.options.verbose
        self.os = re.sub ('[-0-9].*', '', self.platform)

        self.target_architecture = platforms[self.platform]
        self.cpu = self.target_architecture.split ('-')[0]
        self.build_source = False
        self.is_distro = (self.platform in distros
                          or self.platform.startswith ('debian'))


        self.gtk_version = '2.8'
        self.tool_prefix = self.target_architecture + '-'
        self.distcc_hosts = ''
        
	if self.target_architecture.startswith ('x86_64'):
	    self.package_arch = 'amd64'
            self.debian_branch = 'unstable'
	else:
            self.package_arch = re.sub ('-.*', '', self.target_architecture)
            self.package_arch = re.sub ('i[0-9]86', 'i386', self.package_arch)
            self.package_arch = re.sub ('arm.*', 'arm', self.package_arch)
#            self.package_arch = re.sub ('powerpc.*', 'ppc', self.package_arch)
            self.debian_branch = 'stable'
        
        self.keep_build = False
        self.use_tools = False

        self.fakeroot_cache = '' # %(builddir)s/fakeroot.save'
        self.fakeroot = 'fakeroot -i%(fakeroot_cache)s -s%(fakeroot_cache)s '

        if not os.path.isdir ('log'):
            os.mkdir ('log')
            
        self.os_interface = oslog.Os_commands (('log/%(platform)s.log'
                                                % self.__dict__),
                                               self.options.verbose)
        self.create_dirs ()
        self.build_architecture = self.os_interface.read_pipe ('gcc -dumpmachine',
                                                               silent=True)[:-1]

        try:
            self.cpu_count_str = '%d' % os.sysconf ('SC_NPROCESSORS_ONLN')
        except ValueError:
            self.cpu_count_str = '1'

        ## make sure we don't confuse build or target system.
        self.LD_LIBRARY_PATH = '%(system_root)s/'
        
    def create_dirs (self): 
        for a in (
            'downloads',
            'logdir',
            'packages',
            'specdir',
            'allsrcdir',
            'statusdir',
            'system_root',
            'core_prefix',
            'cross_prefix',
            'targetdir',
            'local_prefix',
            'gubdir',

            'cross_packages',
            'cross_statusdir',
            'cross_allsrcdir',
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

