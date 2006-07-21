import os
import gub
import misc
import re
import imp
import md5
import cross

from new import classobj


class TargetBuildSpec (gub.BuildSpec):
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

    def install (self):
        self.pre_install_libtool_fixup ()
        gub.BuildSpec.install (self)

    def pre_install_libtool_fixup (self):
        ## Workaround for libtool bug.
        ## libtool inserts -L/usr/lib into command line, but this is
        ## on the target system. It will try link in libraries from
        ## /usr/lib/ on the build system. This seems to be problematic for libltdl.a and libgcc.a on MacOS.
        ##
        for lt in self.locate_files ("%(builddir)s", '*.la'):
            lt = lt.strip()
            if not lt:
                continue

            dir = os.path.split (lt)[0]
            suffix = "/.libs"
            if re.search("\\.libs$", dir):
                suffix = ''
            self.file_sub ([
                ("libdir='/usr/lib'", "libdir='%(dir)s%(suffix)s'"),
                #(' -rpath /usr/lib', '')
                ],
                   lt, env=locals ())

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
            self.dump (self.config_cache_settings (), cache_file)
            os.chmod (self.expand (cache_file), 0755)

    def config_cache_settings (self):
        return self.config_cache_overrides (cross_config_cache['all']
                                            + cross_config_cache[self.settings.platform])

    def compile_command (self):
        c = gub.BuildSpec.compile_command (self)
        if (self.settings.cross_distcc_hosts
            and not self.broken_for_distcc ()
            and re.search (r'\bmake\b', c)):
            
            jobs = '-j%d ' % (2*len (self.settings.cross_distcc_hosts.split (' ')))
            c = re.sub (r'\bmake\b', 'make ' + jobs, c)

            ## do this a little complicated: we don't want a trace of
            ## distcc during configure.
            c = 'DISTCC_HOSTS="%s" %s' % (self.settings.cross_distcc_hosts , c)
            c = 'PATH="%(cross_distcc_bindir)s:$PATH" ' + c
            
        return c
            
    def configure (self):
        self.config_cache ()
        gub.BuildSpec.configure (self)

    ## FIXME: this should move elsewhere , as it's not
    ## package specific
    def get_substitution_dict (self, env={}):
        dict = {
            'AR': '%(tool_prefix)sar',
            'AS': '%(tool_prefix)sas',
            'CC': '%(tool_prefix)sgcc %(target_gcc_flags)s',
            'CC_FOR_BUILD': 'C_INCLUDE_PATH= CPPFLAGS= LIBRARY_PATH= cc',
            'CCLD_FOR_BUILD': 'C_INCLUDE_PATH= CPPFLAGS= LIBRARY_PATH= cc',


            ## %(system_root)s/usr/include is already done by
            ## GCC --with-sysroot config, but we  have to be sure
            ## note that overrides some headers in sysroot/usr/include,
            ## which is why setting C_INCLUDE_PATH breaks on FreeBSD. 
            ## 
            ## no %(buildtools)s/usr/include, as this will interfere
            ## with target headers.
            ## The flex header has to be copied into the target compile manually.
            ##
            'C_INCLUDE_PATH': '',
            'CPLUS_INCLUDE_PATH': '',
            'CXX':'%(tool_prefix)sg++ %(target_gcc_flags)s',

            ## UGH -- should be done elsewhere.
            'FREETYPE_CONFIG': '''%(system_root)s/usr/bin/freetype-config \
--prefix=%(system_root)s/usr \
''',
#--urg-broken-if-set-exec-prefix=%(system_root)s/usr \
## ugh, creeping -L/usr/lib problem
## trying revert to LDFLAGS...
##                        'LIBRARY_PATH': '%(system_root)s/usr/lib:%(system_root)s/usr/bin',

# FIXME: usr/bin and w32api belongs to mingw/cygwin; but overriding is broken
            'LDFLAGS': '-L%(system_root)s/usr/lib -L%(system_root)s/usr/bin -L%(system_root)s/usr/lib/w32api',
            'LD': '%(tool_prefix)sld',
            'NM': '%(tool_prefix)snm',
            'PKG_CONFIG_PATH': '%(system_root)s/usr/lib/pkgconfig',
            'PATH': '%(crossprefix)s/bin:%(buildtools)s/bin:' + os.environ['PATH'],
            'PKG_CONFIG': '''pkg-config \
--define-variable prefix=%(system_root)s/usr \
--define-variable includedir=%(system_root)s/usr/include \
--define-variable libdir=%(system_root)s/usr/lib \
''',
            'RANLIB': '%(tool_prefix)sranlib',
            'SED': 'sed', # libtool (expat mingw) fixup
            }

        dict.update (env)
        d =  gub.BuildSpec.get_substitution_dict (self, dict).copy()
        return d


cross_config_cache = {
    'local': '',
    'all': '''

ac_16bit_type=${ac_16bit_type=short}
ac_32bit_type=${ac_32bit_type=int}
ac_64bit_type=${ac_64bit_type=none}
ac_cv_c_long_size_t=${ac_cv_c_long_size_t=no}
ac_cv_c_long_time_t=${ac_cv_c_long_time_t=yes}
ac_cv_c_stack_direction=${ac_cv_c_stack_direction=-1}
ac_cv_exeext=${ac_cv_exeext=}
ac_cv_func_getpgrp_void=${ac_cv_func_getpgrp_void=yes}
ac_cv_func_select=${ac_cv_func_select=yes} # but in mingw only if winsock2.h
ac_cv_func_setvbuf_reversed=${ac_cv_func_setvbuf_reversed=no}
ac_cv_lib_dld_shl_load=${ac_cv_lib_dld_shl_load=no}
ac_cv_search_dlopen=${ac_cv_search_dlopen="none required"}
ac_cv_sizeof___int64=${ac_cv_sizeof___int64=0}
ac_cv_sizeof_char=${ac_cv_sizeof_char=1}
ac_cv_sizeof_char_p=${ac_cv_sizeof_char_p=4}
ac_cv_sizeof_double=${ac_cv_sizeof_double=8}
ac_cv_sizeof_float=${ac_cv_sizeof_float=4}
ac_cv_sizeof_int=${ac_cv_sizeof_int=4}
ac_cv_sizeof_intmax_t=${ac_cv_sizeof_intmax_t=8}
ac_cv_sizeof_intptr_t=${ac_cv_sizeof_intptr_t=4}
ac_cv_sizeof_long=${ac_cv_sizeof_long=4}
ac_cv_sizeof_long_double=${ac_cv_sizeof_long_double=12}
ac_cv_sizeof_long_long=${ac_cv_sizeof_long_long=8}
ac_cv_sizeof_ptrdiff_t=${ac_cv_sizeof_ptrdiff_t=4}
ac_cv_sizeof_short=${ac_cv_sizeof_short=2}
ac_cv_sizeof_size_t=${ac_cv_sizeof_size_t=4}
ac_cv_sizeof_uintptr_t=${ac_cv_sizeof_uintptr_t=4}
ac_cv_sizeof_unsigned___int64=${ac_cv_sizeof_unsigned___int64=0}
ac_cv_sizeof_unsigned_char=${ac_cv_sizeof_unsigned_char=1}
ac_cv_sizeof_unsigned_int=${ac_cv_sizeof_unsigned_int=4}
ac_cv_sizeof_unsigned_long=${ac_cv_sizeof_unsigned_long=4}
ac_cv_sizeof_unsigned_long_long=${ac_cv_sizeof_unsigned_long_long=8}
ac_cv_sizeof_unsigned_short=${ac_cv_sizeof_unsigned_short=2}
ac_cv_sizeof_void_p=${ac_cv_sizeof_void_p=4}
ac_cv_spinlocks=${ac_cv_spinlocks=no}
ac_cv_sprintf_count=${ac_cv_sprintf_count=yes}
ac_cv_sys_restartable_syscalls=${ac_cv_sys_restartable_syscalls=yes}
ac_exeext=${ac_exeext=}

# libtool searches not only in the cross libpath
#     /cygwin/usr/lib:/cygwin/usr/lib/w32api:/usr/i686-cygwin/lib
# but also in /usr/lib.  there it finds libdl.a and adds -ldl
# to LIBS
# it seems that libtool is broken wrt cross compilation:
#    sys_lib_search_path_spec="/usr/lib /lib/w32api /lib /usr/local/lib"
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/lib"'"}

lt_cv_dlopen=${lt_cv_dlopen="dlopen"}
''',
    'arm' : '''
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}

glib_cv_uscore=${glib_cv_uscore=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
##libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/usr/lib"'"}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/lib"'"}
''',
    'mipsel' : '''
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}

glib_cv_uscore=${glib_cv_uscore=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
##libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/usr/lib"'"}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/lib"'"}
''',
    'freebsd' : '''
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=no}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}

glib_cv_uscore=${glib_cv_uscore=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-lc"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
##libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/lib "'"}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/lib "'"}
''',
    'linux' : '''
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=yes}

glib_cv_uscore=${glib_cv_uscore=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="-ldl"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=32768}
##libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/usr/lib"'"}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/lib"'"}
''',
    'darwin-ppc' : '''
ac_cv_c_bigendian=${ac_cv_c_bigendian=yes}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_type_socklen_t=${ac_cv_type_socklen_t=yes}

glib_cv_uscore=${glib_cv_uscore=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
''',
    'darwin-x86' : '''
ac_cv_c_bigendian=${ac_cv_c_bigendian=no}
ac_cv_func_posix_getpwuid_r=${ac_cv_func_posix_getpwuid_r=yes}
ac_cv_type_socklen_t=${ac_cv_type_socklen_t=yes}

glib_cv_uscore=${glib_cv_uscore=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
''',
    'cygwin': '''
ac_cv_func_mkfifo=${ac_cv_func_mkfifo=yes}
ac_cv_have_dev_ptc=${ac_cv_have_dev_ptc=}
ac_cv_have_dev_ptmx=${ac_cv_have_dev_ptmx=}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/usr/lib/w32api %(system_root)s/lib"'"}
''',
    'mingw': '''
ac_cv_func_malloc_0_nonnull=${ac_cv_func_malloc_0_nonnull=yes}
ac_cv_func_memcmp_working=${ac_cv_func_memcmp_working=yes}
ac_cv_func_mkfifo=${ac_cv_func_mkfifo=no}
ac_cv_func_stat_empty_string_bug=${ac_cv_func_stat_empty_string_bug=no}
ac_cv_have_dev_ptc=${ac_cv_have_dev_ptc=no}
ac_cv_have_dev_ptmx=${ac_cv_have_dev_ptmx=no}
ac_cv_lib_dl_dlopen=${ac_cv_lib_dl_dlopen=no}

lt_cv_dlopen_libs=${lt_cv_dlopen_libs="none required"}
lt_cv_sys_max_cmd_len=${lt_cv_sys_max_cmd_len=8192}
libltdl_cv_sys_search_path=${libltdl_cv_sys_search_path="'"%(system_root)s/usr/lib %(system_root)s/usr/lib/w32api %(system_root)s/lib"'"}
'''
}

cross_config_cache['debian'] = cross_config_cache['linux']


def load_target_package (settings, url):
    """
    Return TargetBuildSpec instance to build package from URL.

    URL can be partly specified (eg: only a name, `lilypond'),
    defaults are taken from the spec file.
    """

    name = os.path.basename (url)
    init_vars = {'format':None, 'version':None, 'url': None,}
    try:
        ball = name
        name, v, format = misc.split_ball (ball)
        ##version = misc.version_to_string (v)
        version, build = v
        if not version:
            name = url
        elif (url.startswith ('/')
            or url.startswith ('file://')
            or url.startswith ('ftp://')
            or url.startswith ('http://')):
            init_vars['url'] = url
        if version:
            init_vars['version'] = '.'.join (version)
        if format:
            init_vars['format'] = '.'.join (version)
    except:
        pass
    file_name = settings.specdir + '/' + name + '.py'
    class_name = (name[0].upper () + name[1:]).replace ('-', '_')
    klass = None
    checksum = '0000'
    
    if os.path.exists (file_name):
        print 'reading spec', file_name

        desc = ('.py', 'U', 1)
        checksum = md5.md5 (open (file_name).read ()).hexdigest ()

        file = open (file_name)
        module = imp.load_module (name, file, file_name, desc)
        full = class_name + '__' + settings.platform.replace ('-', '__')

        d = module.__dict__
        while full:
            if d.has_key (full):
                klass = d[full]
                break
            full = full[:max (full.rfind ('__'), 0)]

        for i in init_vars.keys ():
            if d.has_key (i):
                init_vars[i] = d[i]
    else:
        ## yes: sucks for cygwin etc. but need this for debugging the rest.
        raise Exception ("no such spec: " + url)
        
    if not klass:
        # Without explicit spec will only work if URL
        # includes version and format, eg,
        # URL=libtool-1.5.22.tar.gz
        klass = classobj (name,
                 (TargetBuildSpec,),
                 {})
    package = klass (settings)
    package.spec_checksum = checksum
    package.cross_checksum = cross.get_cross_checksum (settings.platform)
    
    if init_vars['version']:
        package.with (version=init_vars['version'])
#                package.with (format=init_vars['format'],
#                              mirror=init_vars['url'],
#                              version=init_vars['version'],

    return package
