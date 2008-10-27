import os
import re
#
from gub import build
from gub import config_cache
from gub import context
from gub import misc
from gub import loggedos

class TargetBuild (build.UnixBuild):
    def __init__ (self, settings, source):
        build.UnixBuild.__init__ (self, settings, source)

    @context.subst_method
    def configure_command_native (self):
        return build.UnixBuild.configure_command (self)

    def configure_command (self):
        return misc.join_lines ('''%(configure_binary)s
--config-cache
--enable-shared
--disable-static
--build=%(build_architecture)s
--host=%(target_architecture)s
--target=%(target_architecture)s
--prefix=%(prefix_dir)s
--sysconfdir=%(prefix_dir)s/etc
--includedir=%(prefix_dir)s/include
--infodir=%(prefix_dir)s/share/info
--mandir=%(prefix_dir)s/share/man
--libdir=%(prefix_dir)s/lib
''')

    def install (self):
        self.pre_install_libtool_fixup ()
        build.UnixBuild.install (self)
        if self.config_script ():
            self.install_config_script ()

    @context.subst_method
    def config_script (self):
        return ''

    def install_config_script (self):
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        self.system ('cp %(install_prefix)s/bin/%(config_script)s %(install_prefix)s%(cross_dir)s/bin/%(config_script)s')
        self.file_sub ([('^prefix=/usr/*\s*$', 'prefix=%(system_prefix)s'),
                        ('( |-I)/usr/include', r'\1%(system_prefix)s/include'),
                        ('( |-L)/usr/lib/* ', r'\1%(system_prefix)s/lib'),
                        ('^includedir=/usr/include/*\s*$', 'includedir=%(system_prefix)s/include'),
                        ('^libdir=/usr/lib/*\s*$', 'libdir=%(system_prefix)s/lib'),],
                       '%(install_prefix)s%(cross_dir)s/bin/%(config_script)s',
                       must_succeed=1)

    def pre_install_libtool_fixup (self):
        ## Workaround for libtool bug.  libtool inserts -L/usr/lib
        ## into command line, but this is on the target system. It
        ## will try link in libraries from /usr/lib/ on the build
        ## system.  This seems to be problematic for libltdl.a and
        ## libgcc.a on MacOS.
        ##
        def fixup (logger, file):
            file = file.strip ()
            if not file:
                return
            dir = os.path.split (file)[0]
            suffix = '/.libs'
            if re.search ('\\.libs$', dir):
                suffix = ''
            
            loggedos.file_sub (logger,
                               [("libdir='/usr/lib'",
                                 self.expand ("libdir='%(dir)s%(suffix)s'",
                                             env=locals ())),
                                ], file)
        self.map_locate (fixup, '%(builddir)s', '*.la')

    def config_cache_settings (self):
        return self.config_cache_overrides (config_cache.config_cache['all']
                                            + config_cache.config_cache[self.settings.platform])

    @context.subst_method
    def compile_command_native (self):
        return 'make %(makeflags_native)s '

    @context.subst_method
    def makeflags_native (self):
        return ''

    def compile_command (self):
        c = build.UnixBuild.compile_command (self)
        if (not self.force_sequential_build () and self.settings.cpu_count_str):
            c = re.sub (r'\bmake\b',
                        'make -j%s '% self.settings.cpu_count_str, c)
        return c
            
    def get_substitution_dict_native (self):
        return build.UnixBuild.get_substitution_dict

    def set_substitution_dict_native (self):
        save = self.get_substitution_dict
        self.get_substitution_dict = misc.bind_method (self.get_substitution_dict_native (), self)
        return save

    def configure_native (self):
        save = self.set_substitution_dict_native ()
        self.system ('''
mkdir -p %(builddir)s || true
cd %(builddir)s && chmod +x %(configure_binary)s && %(configure_command_native)s
''')
        self.get_substitution_dict = save

    def compile_native (self):
        save = self.set_substitution_dict_native ()
        self.system ('cd %(builddir)s && %(compile_command_native)s')
        self.get_substitution_dict = save

    ## FIXME: this should move elsewhere , as it's not
    ## package specific
    def get_substitution_dict (self, env={}):
        dict = {
            'AR': '%(toolchain_prefix)sar',
            'AS': '%(toolchain_prefix)sas',
            'CC': '%(toolchain_prefix)sgcc %(target_gcc_flags)s',
            'CC_FOR_BUILD': 'C_INCLUDE_PATH= CPATH= CPPFLAGS= LIBRARY_PATH= cc',
            'CCLD_FOR_BUILD': 'C_INCLUDE_PATH= CPATH= CPPFLAGS= LIBRARY_PATH= cc',
#preliminary
#            'LDFLAGS_FOR_BUILD': '',
            

            ## %(system_prefix)s/include is already done by
            ## GCC --with-sysroot config, but we  have to be sure
            ## note that overrides some headers in sysroot/usr/include,
            ## which is why setting C_INCLUDE_PATH breaks on FreeBSD. 
            ## 
            ## no %(toolchain_prefix)s/usr/include, as this will interfere
            ## with target headers.
            ## The flex header has to be copied into the target compile manually.
            ##
            'C_INCLUDE_PATH': '',
            'CPATH': '',
            'CPLUS_INCLUDE_PATH': '',
            'CXX':'%(toolchain_prefix)sg++ %(target_gcc_flags)s',

#--urg-broken-if-set-exec-prefix=%(system_prefix)s \
## ugh, creeping -L/usr/lib problem
## trying revert to LDFLAGS...
##                        'LIBRARY_PATH': '%(system_prefix)s/lib:%(system_prefix)s/bin',
            'LIBRARY_PATH': '',
# FIXME: usr/bin and w32api belongs to mingw/cygwin; but overriding is broken
#            'LDFLAGS': '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api',
            'LDFLAGS': '',
            'LD': '%(toolchain_prefix)sld',
            'LD_LIBRARY_PATH': '%(tools_prefix)s/lib'
            + misc.append_path (os.environ.get ('LD_LIBRARY_PATH', '')),
            'NM': '%(toolchain_prefix)snm',
            'PKG_CONFIG_PATH': '%(system_prefix)s/lib/pkgconfig',
            'PATH': '%(cross_prefix)s/bin:%(toolchain_prefix)s/bin:' + os.environ['PATH'],
            'PKG_CONFIG': '''pkg-config \
--define-variable prefix=%(system_prefix)s \
--define-variable includedir=%(system_prefix)s/include \
--define-variable libdir=%(system_prefix)s/lib \
''',
            'RANLIB': '%(toolchain_prefix)sranlib',
            'SED': 'sed', # libtool (expat mingw) fixup
            }

        # FIXME: usr/bin and w32api belongs to mingw/cygwin; but overriding is broken
        # FIXME: how to move this to cygwin.py/mingw.py?
        # Hmm, better to make wrappers for gcc/c++/g++ that add options;
        # see (gub-samco branch) linux-arm-vfp.py?
        if self.settings.platform in ('cygwin', 'mingw'):
            dict['LDFLAGS'] = '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api'

        #FIXME: how to move this to arm.py?
        if self.settings.target_architecture == 'armv5te-softfloat-linux':
            dict['CFLAGS'] = '-O'

        dict.update (env)
        d = build.UnixBuild.get_substitution_dict (self, dict).copy ()
        return d

class MakeBuild (TargetBuild):
    def stages (self):
        return ['shadow' for s in [s for s in ToolsBuild.stages () if s not in ['autoupdate']]
                if s == 'configure']

class PythonBuild (TargetBuild):
    def stages (self):
        return [s for s in TargetBuild.stages () if s not in ['autoupdate', 'configure']]
    def compile (self):
        self.system ('mkdir -p %(builddir)s')
    def install_command (self):
        return 'python %(srcdir)s/setup.py install --prefix=%(tools_prefix)s --root=%(install_root)s'

class SConsBuild (TargetBuild):
    def stages (self):
        return [s for s in TargetBuild.stages () if s not in ['autoupdate', 'configure']]
    def compile_command (self):
        # SCons barfs on trailing / on directory names
        return ('scons PREFIX=%(system_prefix)s'
                ' PREFIX_DEST=%(install_root)s')
    def install_command (self):
        return self.compile_command () + ' install'

class Change_target_dict:
    def __init__ (self, package, override):
        self._target_dict_method = package.get_substitution_dict
        self._add_dict = override

    def target_dict (self, env={}):
        env_copy = env.copy ()
        env_copy.update (self._add_dict)
        d = self._target_dict_method (env_copy)
        return d

    def append_dict (self, env={}):
        d = self._target_dict_method ()
        for (k, v) in self._add_dict.items ():
            d[k] += v
        d.update (env)
        d = context.recurse_substitutions (d)
        return d

def change_target_dict (package, add_dict):
    """Override the get_substitution_dict () method of PACKAGE."""
    try:
        package.get_substitution_dict = Change_target_dict (package, add_dict).target_dict
    except AttributeError:
        pass

def append_target_dict (package, add_dict):
    """Override the get_substitution_dict () method of PACKAGE."""
    try:
        package.get_substitution_dict = Change_target_dict (package, add_dict).append_dict
    except AttributeError:
        pass

