import gub
import misc
import glob
import os
import imp
import md5

from context import subst_method 
class CrossToolSpec (gub.BuildSpec):
    """Package for cross compilers/linkers etc.
    """

    def configure_command (self):
        return (gub.BuildSpec.configure_command (self)
            + misc.join_lines ('''
--program-prefix=%(target_architecture)s-
--prefix=%(cross_prefix)s/
--with-slibdir=/usr/lib/
--target=%(target_architecture)s
--with-sysroot=%(system_root)s/
'''))

    def compile_command (self):
        return self.native_compile_command ()
        
    def install_command (self):
        return '''make DESTDIR=%(install_root)s prefix=/usr/cross/ install'''

    def gub_src_uploads (self):
        return '%(gub_cross_uploads)s'

    def get_subpackage_names (self):
        return ['doc', '']
    
class Binutils (CrossToolSpec):
    def install (self):
        CrossToolSpec.install (self)
        self.system ('rm %(install_root)s/usr/cross/lib/libiberty.a')
    
class Gcc (CrossToolSpec):
    def get_build_dependencies (self):
        return ['binutils']

    @subst_method
    def NM_FOR_TARGET(self):
         return "%(tool_prefix)snm"

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
            target = self.expand ('%(install_prefix)s/%(dir)s', locals())
            if not os.path.isdir (target):
                os.makedirs (target)
            self.system ('mv %(f)s %(install_prefix)s/lib', locals())

    def install (self):
        CrossToolSpec.install (self)
        old_libs = self.expand ('%(install_root)s/usr/cross/%(target_architecture)s')

        self.move_target_libs (old_libs)
        self.move_target_libs (self.expand ('%(install_root)s/usr/cross/lib'))
        ## FIXME: .so senseless for darwin.
        self.system ('''
cd %(install_root)s/usr/lib && ln -fs libgcc_s.so.1 libgcc_s.so
''')



def change_target_packages (package_object_dict):
    pass

class MethodOverrider:
    """UGH, python closures don't work reliably?"""
    
    def __init__ (self, old_func, new_func, extra_args):
        self.new_func = new_func
        self.old_func = old_func
        self.args = extra_args
    def method (self):
        all_args = (self.old_func (),) + self.args  
        return apply (self.new_func, all_args)

def set_cross_dependencies (package_object_dict):
    packs = package_object_dict.values ()
    cross_packs = [p for p in packs if isinstance (p, CrossToolSpec)]
    sdk_packs = [p for p in packs if isinstance (p, gub.SdkBuildSpec)]
    other_packs = [p for p in packs if (not isinstance (p, CrossToolSpec)
                                        and not isinstance (p, gub.SdkBuildSpec)
                                        and not isinstance (p, gub.BinarySpec))]
    
    sdk_names = [s.name() for s in sdk_packs]
    cross_names = [s.name() for s in cross_packs]

    for p in other_packs:
        old_callback = p.get_build_dependencies
        p.get_build_dependencies = MethodOverrider (old_callback,
                                                    lambda x,y: x+y, (cross_names,)).method

    for p in other_packs + cross_packs:
        old_callback = p.get_build_dependencies
        p.get_build_dependencies = MethodOverrider (old_callback,
                                                    lambda x,y: x+y, (sdk_names,)).method

    return packs

def set_framework_ldpath (packs):
    for c in packs:
        change = gub.Change_target_dict (c, {'LDFLAGS': r" -Wl,--rpath,'$${ORIGIN}/../lib/' "})
        c.get_substitution_dict = change.append_dict

cross_module_checksums = {}
def get_cross_module (platform):
    base = platform
    try:
        base = {
            'darwin-ppc':'darwintools',
            'darwin-x86':'darwintools',
            'local':'tools'}[platform]
    except KeyError:
        pass
    
    desc = ('.py', 'U', 1)
    file_name = 'lib/%s.py' % base
    file = open (file_name)
    print 'module-name: ' + file_name
    module = imp.load_module (base, file, file_name, desc)

    cross_module_checksums[platform] = md5.md5 (open (file_name).read ()).hexdigest ()
    
    return module

def get_cross_packages (settings):
    mod = get_cross_module (settings.platform)
    return mod.get_cross_packages (settings)

def get_cross_checksum (platform):
    try:
        return cross_module_checksums[platform]
    except KeyError:
        print 'No cross module found'
        return '0000'

