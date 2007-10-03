from gub import build
from gub import misc
from gub import context

class CrossToolsBuild (build.UnixBuild):
    """Package for cross compilers/linkers etc.
    """
    def configure_command (self):
        return (build.UnixBuild.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(target_architecture)s-
--prefix=%(cross_prefix)s
--with-slibdir=/usr/lib
--target=%(target_architecture)s
--with-sysroot=%(system_root)s
--disable-multilib
'''))
    def compile_command (self):
        return self.native_compile_command ()
    def install_command (self):
        return '''make DESTDIR=%(install_root)s prefix=/usr/cross install'''
    def get_subpackage_names (self):
        return ['doc', '']
    def install_license (self):
        self.harmless ('not installing license file for cross package: %(name)s' % self.get_substitution_dict ())

def change_target_package (package):
    pass

def set_cross_dependencies (package_object_dict):
    packs = package_object_dict.values ()
    cross_packs = [p for p in packs if isinstance (p, CrossToolsBuild)]
    sdk_packs = [p for p in packs if isinstance (p, build.SdkBuild)]
    other_packs = [p for p in packs if (not isinstance (p, CrossToolsBuild)
                                        and not isinstance (p, build.SdkBuild)
                                        and not isinstance (p, build.BinaryBuild))]
    
    sdk_names = [s.name() for s in sdk_packs]
    cross_names = [s.name() for s in cross_packs]
    for p in other_packs:
        old_callback = p.get_build_dependencies
        p.get_build_dependencies = misc.MethodOverrider (old_callback,
                                                         lambda x,y: x+y, (cross_names,))

    for p in other_packs + cross_packs:
        old_callback = p.get_build_dependencies
        p.get_build_dependencies = misc.MethodOverrider (old_callback,
                                                         lambda x,y: x+y, (sdk_names,))

    return packs

cross_module_checksums = {}
cross_module_cache = {}
def get_cross_module (settings):
    platform = settings.platform
    if cross_module_cache.has_key (platform):
        return cross_module_cache[platform]

    import re
    base = re.sub ('[-0-9].*', '', platform)
    for name in platform, base:
        file_name = 'gub/%(name)s.py' % locals ()
        import os
        if os.path.exists (file_name):
            break
    settings.os_interface.info ('module-name: ' + file_name + '\n')
    import misc
    module = misc.load_module (file_name, base)

    import md5
    cross_module_checksums[platform] = md5.md5 (open (file_name).read ()).hexdigest ()
    cross_module_cache[platform] = module
    return module

def get_cross_packages (settings):
    mod = get_cross_module (settings)
    return mod.get_cross_packages (settings)

def get_build_dependencies (settings):
    mod = get_cross_module (settings)
    return mod.get_cross_build_dependencies (settings)

def get_cross_checksum (platform):
    try:
        return cross_module_checksums[platform]
    except KeyError:
        print 'No cross module found'
        return '0000'

def setup_linux_x86 (package):
    '''
Hack for using 32 bit compiler on linux-64.

Use linux-x86 cross compiler to compile non-64-bit-clean packages such
as nsis and odcctools.  A plain 32 bit compiler could also be used,
but we do not have such a beast.  Make sure to have 32-bit
compatibility installed:
    apt-get install ia32-libs
'''
    import os
    x86_dir = package.settings.alltargetdir + '/linux-x86'
    x86_cross = (x86_dir
                 + package.settings.root_dir
                 + package.settings.prefix_dir
                 + package.settings.cross_dir)
    x86_bindir = x86_cross + '/bin'
    x86_cross_bin = x86_cross + '/i686-linux' + '/bin'
    package.PATH = x86_cross_bin + ':' + os.environ['PATH']
    package.LIBRESTRICT_ALLOW = package.settings.targetdir
    package.CC = x86_cross_bin + '/gcc'
    package.CXX = x86_cross_bin + '/g++'

    compiler = x86_bindir + '/i686-linux-gcc'
    if not os.path.exists (compiler):
        print 'error: cannot find 32 bit compiler: %(compiler)s\n' % locals ()
        raise Exception ('Package %s depends on target/linux-x86.'
                         % package.__class__)
    if os.system ('''echo 'int main () { return 0; }' > 32bit.c && %(compiler)s -o 32bit 32bit.c && ./32bit''' % locals ()):
        print 'error: cannot run 32 bit executable: 32bit\n'
        raise Exception ('Package %s depends on 32 bit libraries'''
                         % package.__class__)
    os.system ('rm -f 32bit 32bit.c')

    def set_env (command):
        return ('PATH=' + package.PATH + ' '
                + 'LIBRESTRICT_ALLOW=' + package.LIBRESTRICT_ALLOW + ' '
                + command)

    package.configure_command \
        = misc.MethodOverrider (package.configure_command, set_env)
    package.compile_command \
        = misc.MethodOverrider (package.compile_command, set_env)
    package.install_command \
        = misc.MethodOverrider (package.install_command, set_env)

    def check_link (src, dest):
        dest = x86_cross_bin + '/' + dest
        if not os.path.exists (dest):
            # duh, must chdir for relative link
            #src = '../../bin/i686-linux-' + src
            src = x86_bindir + '/i686-linux-' + src
            os.link (src, dest)
    check_link ('cpp', 'cpp')
    check_link ('gcc', 'cc')
    check_link ('g++', 'c++')
    check_link ('gcc', 'gcc')
    check_link ('g++', 'g++')
