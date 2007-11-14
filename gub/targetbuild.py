import os
import re

from gub import build
from gub import context
from gub import misc

class TargetBuild (build.UnixBuild):
    def __init__ (self, settings, source):
        build.UnixBuild.__init__ (self, settings, source)

    def configure_command (self):
        return misc.join_lines ('''%(srcdir)s/configure
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

    def pre_install_libtool_fixup (self):
        ## Workaround for libtool bug.  libtool inserts -L/usr/lib
        ## into command line, but this is on the target system. It
        ## will try link in libraries from /usr/lib/ on the build
        ## system.  This seems to be problematic for libltdl.a and
        ## libgcc.a on MacOS.
        ##
        def fixup (file):
            file = file.strip ()
            if not file:
                return
            dir = os.path.split (file)[0]
            suffix = '/.libs'
            if re.search ('\\.libs$', dir):
                suffix = ''
            self.file_sub ([
                ("libdir='/usr/lib'", "libdir='%(dir)s%(suffix)s'"),
                ],
                   file, env=locals ())
        self.map_locate (fixup, '%(builddir)s', '*.la')

    ## UGH. only for cross!
    def config_cache_overrides (self, str):
        return str

    def config_cache_settings (self):
        return self.config_cache_overrides (self, '')

    def config_cache (self):
        str = self.config_cache_settings ()
        if str:
            self.system ('mkdir -p %(builddir)s')
            cache_file = '%(builddir)s/config.cache'
            self.dump (self.config_cache_settings (), cache_file, permissions=0755)

    def config_cache_settings (self):
        from gub import config_cache
        return self.config_cache_overrides (config_cache.config_cache['all']
                                            + config_cache.config_cache[self.settings.platform])

    def compile_command (self):
        c = build.UnixBuild.compile_command (self)
        if (self.settings.cross_distcc_hosts
            and not self.force_sequential_build ()
            and re.search (r'\bmake\b', c)):
            
            jobs = '-j%d ' % (2*len (self.settings.cross_distcc_hosts.split (' ')))
            c = re.sub (r'\bmake\b', 'make ' + jobs, c)

            ## do this a little complicated: we don't want a trace of
            ## distcc during configure.
            c = 'DISTCC_HOSTS="%s" %s' % (self.settings.cross_distcc_hosts , c)
            c = 'PATH="%(cross_distcc_bindir)s:$PATH" ' + c
        elif (not self.force_sequential_build ()
              and self.settings.cpu_count_str):
            c = re.sub (r'\bmake\b', 'make -j%s '% self.settings.cpu_count_str, c)

        return c
            
    def configure (self):
        self.config_cache ()
        build.UnixBuild.configure (self)

    ## FIXME: this should move elsewhere , as it's not
    ## package specific
    def get_substitution_dict (self, env={}):
        dict = {
            'AR': '%(toolchain_prefix)sar',
            'AS': '%(toolchain_prefix)sas',
            'CC': '%(toolchain_prefix)sgcc %(target_gcc_flags)s',
            'CC_FOR_BUILD': 'C_INCLUDE_PATH= CPATH= CPPFLAGS= LIBRARY_PATH= cc',
            'CCLD_FOR_BUILD': 'C_INCLUDE_PATH= CPATH= CPPFLAGS= LIBRARY_PATH= cc',


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

