import os
from gub import gubb
from gub import misc
import re
import imp
import md5
from gub import cross

from context import subst_method

class TargetBuildSpec (gubb.BuildSpec):
    def configure_command (self):
        return misc.join_lines ('''%(srcdir)s/configure
--config-cache
--enable-shared
--disable-static
--build=%(build_architecture)s
--host=%(target_architecture)s
--target=%(target_architecture)s
--prefix=/usr
--sysconfdir=/usr/etc
--includedir=/usr/include
--infodir=/usr/share/info
--mandir=/usr/share/man
--libdir=/usr/lib
''')

    def __init__ (self, settings):
        gubb.BuildSpec.__init__ (self, settings)

    def install (self):
        self.pre_install_libtool_fixup ()
        gubb.BuildSpec.install (self)

    def pre_install_libtool_fixup (self):
        ## Workaround for libtool bug.
        ## libtool inserts -L/usr/lib into command line, but this is
        ## on the target system. It will try link in libraries from
        ## /usr/lib/ on the build system. This seems to be problematic for libltdl.a and libgcc.a on MacOS.
        ##
        def fixup (file):
            file = file.strip ()
            if not file:
                return
            dir = os.path.split (file)[0]
            suffix = '/.libs'
            if re.search('\\.libs$', dir):
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
        c = gubb.BuildSpec.compile_command (self)
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
        gubb.BuildSpec.configure (self)

    ## FIXME: this should move elsewhere , as it's not
    ## package specific
    def get_substitution_dict (self, env={}):
        dict = {
            'AR': '%(tool_prefix)sar',
            'AS': '%(tool_prefix)sas',
            'CC': '%(tool_prefix)sgcc %(target_gcc_flags)s',
            'CC_FOR_BUILD': 'C_INCLUDE_PATH= CPATH= CPPFLAGS= LIBRARY_PATH= cc',
            'CCLD_FOR_BUILD': 'C_INCLUDE_PATH= CPATH= CPPFLAGS= LIBRARY_PATH= cc',


            ## %(system_root)s/usr/include is already done by
            ## GCC --with-sysroot config, but we  have to be sure
            ## note that overrides some headers in sysroot/usr/include,
            ## which is why setting C_INCLUDE_PATH breaks on FreeBSD. 
            ## 
            ## no %(local_prefix)s/usr/include, as this will interfere
            ## with target headers.
            ## The flex header has to be copied into the target compile manually.
            ##
            'C_INCLUDE_PATH': '',
            'CPATH': '',
            'CPLUS_INCLUDE_PATH': '',
            'CXX':'%(tool_prefix)sg++ %(target_gcc_flags)s',

#--urg-broken-if-set-exec-prefix=%(system_root)s/usr \
## ugh, creeping -L/usr/lib problem
## trying revert to LDFLAGS...
##                        'LIBRARY_PATH': '%(system_root)s/usr/lib:%(system_root)s/usr/bin',
            'LIBRARY_PATH': '',
# FIXME: usr/bin and w32api belongs to mingw/cygwin; but overriding is broken
#            'LDFLAGS': '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api',
            'LDFLAGS': '',
            'LD': '%(tool_prefix)sld',
            'NM': '%(tool_prefix)snm',
            'PKG_CONFIG_PATH': '%(system_root)s/usr/lib/pkgconfig',
            'PATH': '%(cross_prefix)s/bin:%(local_prefix)s/bin:' + os.environ['PATH'],
            'PKG_CONFIG': '''pkg-config \
--define-variable prefix=%(system_root)s/usr \
--define-variable includedir=%(system_root)s/usr/include \
--define-variable libdir=%(system_root)s/usr/lib \
''',
            'RANLIB': '%(tool_prefix)sranlib',
            'SED': 'sed', # libtool (expat mingw) fixup
            }

        # FIXME: usr/bin and w32api belongs to mingw/cygwin; but overriding is broken
        # FIXME: how to move this to cygwin.py/mingw.py?
        # Hmm, better to make wrappers for gcc/c++/g++ that add options;
        # see (gub-samco branch) linux-arm-vfp.py?
        if self.settings.platform in ('cygwin', 'mingw'):
            dict['LDFLAGS'] = '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api'

        #FIXME: how to move this to arm.py?
        if self.settings.target_architecture == 'armv5te-softfloat-linux':
            dict['CFLAGS'] = '-O'

        dict.update (env)
        d = gubb.BuildSpec.get_substitution_dict (self, dict).copy ()
        return d

def get_build_spec (settings, url):
    """
    Return TargetBuildSpec instance to build package from URL.

    URL can be partly specified (eg: only a name, `lilypond'),
    defaults are taken from the spec file.
    """

    package = gubb.get_build_spec (TargetBuildSpec, settings, url)
    crossmod = cross.get_cross_module (settings)
    crossmod.change_target_package (package)
    return package
    
