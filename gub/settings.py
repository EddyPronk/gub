import os
import re
import optparse

from gub import build
from gub import context
from gub import mirrors
from gub import misc
from gub import sources
from gub import loggedos
from gub import logging

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

    'linux-arm': 'arm-linux',
    'linux-arm-softfloat': 'armv5te-softfloat-linux',
    'linux-arm-vfp': 'arm-linux',

    'linux-mipsel': 'mipsel-linux',

    'linux-x86': 'i686-linux',
    'linux-64': 'x86_64-linux',
    'linux-ppc': 'powerpc-linux',
    'tools': 'tools',
    'mingw': 'i686-mingw32',
}

distros = ('cygwin')

class UnknownPlatform (Exception):
    pass

def get_platform_from_dir (settings, dir):
    m = re.match ('.*?([^/]+)(' + settings.root_dir + ')?/*$', dir)
    if m:
        return m.group (1)
    return None

class Settings (context.Context):
    def __init__ (self, platform):
        context.Context.__init__ (self)

        # TODO: tools-prefix, target-prefix, cross-prefix?
        self.prefix_dir = '/usr'
        self.root_dir = '/root'
        self.cross_dir = '/cross'


        self.platform = platform
        if self.platform not in platforms.keys ():
            raise UnknownPlatform (self.platform)

        GUB_TOOLS_PREFIX = os.environ.get ('GUB_TOOLS_PREFIX')
        
        # config dirs

        if self.platform == 'tools' and GUB_TOOLS_PREFIX:
            self.prefix_dir = ''

        # gubdir is top of `installed' gub repository
        ## self.gubdir = os.getcwd ()
        self.gubdir = os.path.dirname (os.path.dirname (__file__))
        if not self.gubdir:
            self.gubdir = os.getcwd ()

        # workdir is top of writable build stuff
        ##self.workdir = os.getcwd ()
        self.workdir = self.gubdir
        
        # gubdir based: fixed repository layout
        self.patchdir = self.gubdir + '/patches'
        self.sourcefiledir = self.gubdir + '/sourcefiles'
        self.specdir = self.gubdir + '/gub/specs'
        self.nsisdir = self.gubdir + '/nsis'

        # workdir based; may be changed
        self.downloads = self.workdir + '/downloads'
        self.alltargetdir = self.workdir + '/target'
        self.targetdir = self.alltargetdir + '/' + self.platform
        self.logdir = self.targetdir + '/log'

        self.system_root = self.targetdir + self.root_dir
        if self.platform == 'tools' and GUB_TOOLS_PREFIX:
            self.system_root = GUB_TOOLS_PREFIX
        self.system_prefix = self.system_root + self.prefix_dir

        ## Patches are architecture dependent, 
        ## so to ensure reproducibility, we unpack for each
        ## architecture separately.
        self.allsrcdir = self.targetdir + '/src'
        self.allbuilddir = self.targetdir + '/build'
        self.statusdir = self.targetdir + '/status'
        self.packages = self.targetdir + '/packages'

        self.uploads = self.workdir + '/uploads'
        self.platform_uploads = self.uploads + '/' + self.platform

        # FIXME: rename to cross_root?
        ##self.cross_prefix = self.system_prefix + self.cross_dir
        self.cross_prefix = self.targetdir + self.root_dir + self.prefix_dir + self.cross_dir
        self.installdir = self.targetdir + '/install'
        self.tools_root = self.alltargetdir + '/tools' + self.root_dir
        self.tools_prefix = self.tools_root + self.prefix_dir
        if GUB_TOOLS_PREFIX:
            self.tools_root = GUB_TOOLS_PREFIX
            self.tools_prefix = GUB_TOOLS_PREFIX

        self.cross_packages = self.packages + self.cross_dir
        self.cross_allsrcdir = self.allsrcdir + self.cross_dir
        self.cross_statusdir = self.statusdir + self.cross_dir

        self.core_prefix = self.cross_prefix + '/core'
        # end config dirs



        self.target_gcc_flags = '' 
        if self.platform == 'darwin-ppc':
            self.target_gcc_flags = '-D__ppc__'
        elif self.platform == 'mingw':
            self.target_gcc_flags = '-mwindows -mms-bitfields'

        self.os = re.sub ('[-0-9].*', '', self.platform)

        self.target_architecture = platforms[self.platform]
        self.cpu = self.target_architecture.split ('-')[0]
        self.build_source = False
        self.is_distro = (self.platform in distros
                          or self.platform.startswith ('debian'))


        self.gtk_version = '2.8'
        self.toolchain_prefix = self.target_architecture + '-'
        
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
        self.create_dirs ()

        # Cheating by not logging this call saves a dependency on os
        # interface.  Not sure what cheating brings us here, why
        # restrict use of the OS interface+logging facility?
        self.build_architecture = loggedos.read_pipe (logging.default_logger,
                                                      'gcc -dumpmachine').strip ()

        try:
            self.cpu_count_str = '%d' % os.sysconf ('SC_NPROCESSORS_ONLN')
        except ValueError:
            self.cpu_count_str = '1'

        ## make sure we don't confuse build or target system.
        self.LD_LIBRARY_PATH = '%(system_root)s'
        
    def create_dirs (self): 
        for a in (
            'allsrcdir',
            'core_prefix',
            'cross_prefix',
            'downloads',
            'gubdir',
            'tools_prefix',
            'logdir',
            'packages',
            'specdir',
            'statusdir',
            'system_root',
            'targetdir',
            'uploads',

            'cross_packages',
            'cross_statusdir',
            'cross_allsrcdir',
            ):
            dir = self.__dict__[a]
            if not os.path.isdir (dir):
                loggedos.makedirs (logging.default_logger, dir)
        
    def dependency_url (self, string):
        # FIXME: read from settings.rc, take platform into account
        name = string.replace ('-', '_')
        return misc.most_significant_in_dict (sources.__dict__, name, '__')

def get_cli_parser ():
    p = optparse.OptionParser ()

    p.usage = '''settings.py [OPTION]...

Print settings and directory layout.

'''
    p.description = 'Grand Unified Builder.  Settings and directory layout.'

    # c&p #10?
    #import gub_options
    #gub_options.add_common_options (platform,branch,verbose)?
    p.add_option ('-p', '--platform', action='store',
                  dest='platform',
                  type='choice',
                  default=None,
                  help='select target platform',
                  choices=platforms.keys ())
    p.add_option ('-B', '--branch', action='append',
                  dest='branches',
                  default=[],
                  metavar='NAME=BRANCH',
                  help='select branch')
    return p

def as_variables (settings):
    lst = []
    for k in settings.__dict__.keys ():
        v = settings.__dict__[k]
        if type (v) == type (str ()):
            lst.append ('%(k)s=%(v)s' % locals ())
    return lst

def main ():
    cli_parser = get_cli_parser ()
    (options, files) = cli_parser.parse_args ()
    if not options.platform or files:
        raise 'barf'
        sys.exit (2)
    settings = Settings (options.platform)
    print '\n'.join (as_variables (settings))

if __name__ == '__main__':
    main ()
