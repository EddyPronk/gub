import os
#
from gub import build
from gub import context
from gub import logging
from gub import misc
from gub import octal
from gub import target
from gub import tools

#"0596d7296c94b2bb9817338b8c1a76da91673fb9"

# v2.5.91 - there was a late 2007 windows fix. Let's try to see if it
# fixes caching problems on vista.
#version = '0dffe625d43c1165f8b84f97e8ba098793e2cf7b'

class Fontconfig (target.AutoBuild):
    '''Generic font configuration library 
Fontconfig is a font configuration and customization library, which
does not depend on the X Window System.  It is designed to locate
fonts within the system and select them according to requirements
specified by applications.'''

    source = 'http://fontconfig.org/release/fontconfig-2.7.3.tar.gz'
    #source = 'git://anongit.freedesktop.org/git/fontconfig?branch=master&revision=' + version
    dependencies = ['libtool', 'expat-devel', 'freetype-devel', 'tools::freetype', 'tools::pkg-config']
        # FIXME: system dir vs packaging install
        ## UGH  - this breaks  on Darwin!
        ## UGH2 - the added /cross/ breaks Cygwin; possibly need
        ## Freetype_config package (see Guile_config, Python_config)
        # FIXME: this is broken.  for a sane target development package,
        # we want /usr/bin/fontconfig-config must survive.
        # While cross building, we create an  <toolprefix>-fontconfig-config
        # and prefer that.
    configure_flags = (target.AutoBuild.configure_flags
                + misc.join_lines ('''
--with-arch=%(target_architecture)s
--with-freetype-config="%(system_prefix)s%(cross_dir)s/bin/freetype-config
--prefix=%(system_prefix)s
"'''))
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        if 'stat' in misc.librestrict ():
            build.add_dict (self, {'LIBRESTRICT_IGNORE': '%(tools_prefix)s/bin/bash:%(tools_prefix)s/bin/make'})
            # build.add_dict (self, {'LIBRESTRICT_VERBOSE': '1'})
    def patch (self):
        self.dump ('\nAC_SUBST(LT_AGE)', '%(srcdir)s/configure.in', mode='a', permissions=octal.o755)
        target.AutoBuild.patch (self)
    @context.subst_method
    def freetype_cflags (self):
        # this is shady: we're using the flags from the tools version
        # of freetype.
        base_config_cmd = self.settings.expand ('%(tools_prefix)s/bin/freetype-config')
        cmd =  base_config_cmd + ' --cflags'
        logging.command ('pipe %s\n' % cmd)
        # ugh, this is utterly broken.  we're reading from the
        # filesystem init time, when freetype-config does not exist
        # yet.
        # return misc.read_pipe (cmd).strip ()
        return '-I%(system_prefix)s/include/freetype2'
    @context.subst_method
    def freetype_libs (self):
        base_config_cmd = self.settings.expand ('%(tools_prefix)s/bin/freetype-config')
        cmd =  base_config_cmd + ' --libs'
        logging.command ('pipe %s\n' % cmd)
        # return misc.read_pipe (cmd).strip ()
        return '-lfreetype -lz'
    def configure (self):
        self.system ('''
rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
        target.AutoBuild.configure (self)
        self.file_sub ([('DOCSRC *=.*', 'DOCSRC=')],
                       '%(builddir)s/Makefile')
    make_flags = ('man_MANS=' # either this, or add something like tools::docbook-utils
                # librestrict: stuff in fc-case, fc-lang,
                # fc-glyphname, fc-arch' is FOR-BUILD and has
                # dependencies .deps/*.Po /usr/include/stdio.h: 
                + ''' 'SUBDIRS=fontconfig src fc-cache fc-cat fc-list fc-match conf.d' ''')
    def compile (self):
        # help fontconfig cross compiling a bit, all CC/LD
        # flags are wrong, set to the target's root
        ## we want native freetype-config flags here. 
        cflags = '-I%(srcdir)s -I%(srcdir)s/src %(freetype_cflags)s' 
        libs = '%(freetype_libs)s'
        relax = ''
        if 'stat' in misc.librestrict ():
            relax = 'LIBRESTRICT_IGNORE=%(tools_prefix)s/bin/bash:%(tools_prefix)s/bin/make '
        for i in ('fc-case', 'fc-lang', 'fc-glyphname', 'fc-arch'):
            self.system ('''
cd %(builddir)s/%(i)s && %(relax)s make "CFLAGS=%(cflags)s" "LIBS=%(libs)s" CPPFLAGS= LD_LIBRARY_PATH=%(tools_prefix)s/lib LDFLAGS=-L%(tools_prefix)s/lib INCLUDES=
''', locals ())
        target.AutoBuild.compile (self)
    def install (self):
        target.AutoBuild.install (self)
        self.dump ('''set FONTCONFIG_FILE=$INSTALLER_PREFIX/etc/fonts/fonts.conf
set FONTCONFIG_PATH=$INSTALLER_PREFIX/etc/fonts
''', 
             '%(install_prefix)s/etc/relocate/fontconfig.reloc')
        
        
class Fontconfig__mingw (Fontconfig):
    def patch (self):
        Fontconfig.patch (self)
        self.file_sub ([('<cachedir>@FC_CACHEDIR@</cachedir>', '')],
                       '%(srcdir)s/fonts.conf.in')

    def configure (self):
        Fontconfig.configure (self)
        self.dump ('''
#define sleep(x) _sleep (x)
''',
                   '%(builddir)s/config.h',
                   mode='a')

class Fontconfig__darwin (Fontconfig):
    configure_flags = (Fontconfig.configure_flags
                         + ' --with-add-fonts=/Library/Fonts,/System/Library/Fonts ')
    def configure (self):
        Fontconfig.configure (self)
        self.file_sub ([('-Wl,[^ ]+ ', '')],
               '%(builddir)s/src/Makefile')

class Fontconfig__linux (Fontconfig):
    def configure (self):
        Fontconfig.configure (self)
        self.file_sub ([
            ('^sys_lib_search_path_spec="/lib/* ',
            'sys_lib_search_path_spec="%(system_prefix)s/lib /lib '),
            # FIXME: typo: dl_search (only dlsearch exists).
            # comment-out for now
            #('^sys_lib_dl_search_path_spec="/lib/* ',
            # 'sys_lib_dl_search_path_spec="%(system_prefix)s/lib /lib ')
            ],
               '%(builddir)s/libtool')

class Fontconfig__freebsd (Fontconfig__linux):
    pass

class Fontconfig__tools (tools.AutoBuild):
    # FIXME: use mi to get to source?
    #source = 'git://anongit.freedesktop.org/git/fontconfig?revision=' + version
    source = 'http://fontconfig.org/release/fontconfig-2.7.3.tar.gz'
    def patch (self):
        self.dump ('\nAC_SUBST(LT_AGE)', '%(srcdir)s/configure.in', mode='a', permissions=octal.o755)
        tools.AutoBuild.patch (self)
    dependencies = ['libtool', 'freetype', 'expat', 'pkg-config']
    make_flags = ('man_MANS=' # either this, or add something like tools::docbook-utils
                + ' DOCSRC="" ')
