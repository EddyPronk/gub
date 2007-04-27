import os
import gub
import misc
import re
import imp
import md5
import cross

from new import classobj

from context import subst_method

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

    def __init__ (self, settings):
        gub.BuildSpec.__init__ (self, settings)

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
        import config_cache
        return self.config_cache_overrides (config_cache.config_cache['all']
                                            + config_cache.config_cache[self.settings.platform])

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
        elif self.settings.cpu_count_str:
            c += ' -j%s '% self.settings.cpu_count_str
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
        d = gub.BuildSpec.get_substitution_dict (self, dict).copy ()
        return d




def load_target_package (settings, url):
    """
    Return TargetBuildSpec instance to build package from URL.

    URL can be partly specified (eg: only a name, `lilypond'),
    defaults are taken from the spec file.
    """

    name = os.path.basename (url)
    init_vars = {'format':None, 'version':None, 'url': None,}
    if 1: #try:
        ball = name
        name, v, format = misc.split_ball (ball)
        version = misc.version_to_string (v)
        if not version:
            name = url
        elif (url.startswith ('/')
              or url.startswith ('file://')
              or url.startswith ('ftp://')
              or url.startswith ('http://')):
            init_vars['url'] = url
        if version:
            init_vars['version'] = version
        if format:
            init_vars['format'] = format
#    except:
#        pass
    
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
#    else:
#        # FIXME: make a --debug-must-have-spec option
#        ## yes: sucks for cygwin etc. but need this for debugging the rest.
#        raise Exception ("no such spec: " + url)
        
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

    # Initialise building target package from url, without spec
    # test:
    # bin/gub -p linux-64 ftp://ftp.gnu.org/pub/gnu/bison/bison-2.3.tar.gz
    if init_vars['version']:
        package.with (format=init_vars['format'],
                      mirror=init_vars['url'],
                      version=init_vars['version'])

    crossmod = cross.get_cross_module (settings.platform)
    crossmod.change_target_package (package)

    return package
