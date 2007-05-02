import os
#
from gub import gubb
from gub import misc

from context import subst_method 
class CrossToolSpec (gubb.BuildSpec):
    """Package for cross compilers/linkers etc.
    """

    def configure_command (self):
        return (gubb.BuildSpec.configure_command (self)
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

#    def gub_src_uploads (self):
#        return '%(gub_cross_uploads)s'

    def get_subpackage_names (self):
        return ['doc', '']
    
    def license_file (self):
        return ''

#FIXME: merge fully with specs/binutils.py
class Binutils (CrossToolSpec):
    def install (self):
        CrossToolSpec.install (self)
        self.system ('rm %(install_root)s/usr/cross/lib/libiberty.a')
    
#FIXME: merge fully with specs/gcc
class Gcc (CrossToolSpec):
    def get_build_dependencies (self):
        return ['cross/binutils']

    @subst_method
    def NM_FOR_TARGET(self):
         return '%(tool_prefix)snm'

    def get_subpackage_names (self):
        # FIXME: why no -devel package?
        return ['doc', 'runtime', '']

    def languages (self):
        return  ['c', 'c++']
        
    def configure_command (self):
        cmd = CrossToolSpec.configure_command (self)
        # FIXME: using --prefix=%(tooldir)s makes this
        # uninstallable as a normal system package in
        # /usr/i686-mingw/
        # Probably --prefix=/usr is fine too

        language_opt = (' --enable-languages=%s '
                        % ','.join (self.languages ()))
        cxx_opt = '--enable-libstdcxx-debug '

        cmd += '''
--with-as=%(cross_prefix)s/bin/%(target_architecture)s-as
--with-ld=%(cross_prefix)s/bin/%(target_architecture)s-ld
--enable-static
--enable-shared '''

        cmd += language_opt
        if 'c++' in self.languages ():
            cmd +=  ' ' + cxx_opt

        return misc.join_lines (cmd)

    def move_target_libs (self, libdir):
        if not os.path.isdir (libdir):
            return

        files = []

        ## .so* because version numbers trail .so extension. 
        for suf in ['.la', '.so*', '.dylib']:
            files += self.locate_files (libdir, 'lib*' + suf)
            
        for f in files:
            (dir, file) = os.path.split (f)
            target = self.expand ('%(install_prefix)s/%(dir)s', locals ())
            if not os.path.isdir (target):
                os.makedirs (target)
            self.system ('mv %(f)s %(install_prefix)s/lib', locals ())

    def install (self):
        CrossToolSpec.install (self)
        old_libs = self.expand ('%(install_root)s/usr/cross/%(target_architecture)s')

        self.move_target_libs (old_libs)
        self.move_target_libs (self.expand ('%(install_root)s/usr/cross/lib'))
        if os.path.exists (self.expand ('cd %(install_root)s/usr/lib/libgcc_s.so.1')):
            # FIXME: .so senseless for darwin.
            self.system ('''
cd %(install_root)s/usr/lib && ln -fs libgcc_s.so.1 libgcc_s.so
''')

def change_target_package (package):
    pass

def set_cross_dependencies (package_object_dict):
    packs = package_object_dict.values ()
    cross_packs = [p for p in packs if isinstance (p, CrossToolSpec)]
    sdk_packs = [p for p in packs if isinstance (p, gubb.SdkBuildSpec)]
    other_packs = [p for p in packs if (not isinstance (p, CrossToolSpec)
                                        and not isinstance (p, gubb.SdkBuildSpec)
                                        and not isinstance (p, gubb.BinarySpec))]
    
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
def get_cross_module (platform):
    if cross_module_cache.has_key (platform):
        return cross_module_cache[platform]

    import re
    desc = ('.py', 'U', 1)

    base = re.sub ('[-0-9].*', '', platform)
    for name in platform, base:
        file_name = 'gub/%(name)s.py' % locals ()
        if os.path.exists (file_name):
            break
    file = open (file_name)
    print 'module-name: ' + file_name
    import imp
    module = imp.load_module (base, file, file_name, desc)

    import md5
    cross_module_checksums[platform] = md5.md5 (open (file_name).read ()).hexdigest ()
    cross_module_cache[platform] = module
    return module

def get_cross_packages (settings):
    mod = get_cross_module (settings.platform)
    return mod.get_cross_packages (settings)

def get_build_dependencies (settings):
    mod = get_cross_module (settings.platform)
    return mod.get_cross_build_dependencies (settings)

def get_cross_checksum (platform):
    try:
        return cross_module_checksums[platform]
    except KeyError:
        print 'No cross module found'
        return '0000'
