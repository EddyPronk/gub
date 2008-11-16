from gub import mirrors
from gub import build
from gub import misc
from gub import targetbuild
from gub import toolsbuild
from gub import repository
from gub import context
from gub import logging

# v2.6.0 plus one commit
version = '0e21b5a4d5609a5dd0f332b412d878b6f1037d29'

class Fontconfig (targetbuild.TargetBuild):
    '''Generic font configuration library 
Fontconfig is a font configuration and customization library, which
does not depend on the X Window System.  It is designed to locate
fonts within the system and select them according to requirements
specified by applications.'''

    source = 'git://anongit.freedesktop.org/git/fontconfig?branch=master&revision=' + version

    @context.subst_method
    def freetype_cflags (self):
        # this is shady: we're using the flags from the tools version
        # of freetype.
        
        base_config_cmd = self.settings.expand ('%(tools_prefix)s/bin/freetype-config')
        cmd =  base_config_cmd + ' --cflags'
        logging.command ('pipe %s\n' % cmd)
        return misc.read_pipe (cmd).strip ()

    @context.subst_method
    def freetype_libs (self):
        base_config_cmd = self.settings.expand ('%(tools_prefix)s/bin/freetype-config')
        cmd =  base_config_cmd + ' --libs'
        logging.command ('pipe %s\n' % cmd)
        return misc.read_pipe (cmd).strip ()

    def get_build_dependencies (self):
        return ['libtool', 'expat-devel', 'freetype-devel']

    def get_dependency_dict (self):
        return {'': ['expat', 'freetype', 'libtool']}

    def configure_command (self):
        # FIXME: system dir vs packaging install

        ## UGH  - this breaks  on Darwin!
        ## UGH2 - the added /cross/ breaks Cygwin; possibly need
        ## Freetype_config package (see Guile_config, Python_config)

        # FIXME: this is broken.  for a sane target development package,
        # we want /usr/bin/fontconfig-config must survive.
        # While cross building, we create an  <toolprefix>-fontconfig-config
        # and prefer that.

        return (targetbuild.TargetBuild.configure_command (self) 
                + misc.join_lines ('''
--with-arch=%(target_architecture)s
--with-freetype-config="%(system_prefix)s/cross/bin/freetype-config
--prefix=%(system_prefix)s
"'''))

    def configure (self):
        self.system ('''
rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
        targetbuild.TargetBuild.configure (self)

        ## FIXME: libtool too old for cross compile
        self.update_libtool ()
        self.file_sub ([('DOCSRC *=.*', 'DOCSRC=')],
                       '%(builddir)s/Makefile')

    def compile (self):

        # help fontconfig cross compiling a bit, all CC/LD
        # flags are wrong, set to the target's root

        ## we want native freetype-config flags here. 
        cflags = '-I%(srcdir)s -I%(srcdir)s/src %(freetype_cflags)s' 
        libs = '%(freetype_libs)s'

        for i in ('fc-case', 'fc-lang', 'fc-glyphname', 'fc-arch'):
            self.system ('''
cd %(builddir)s/%(i)s && make "CFLAGS=%(cflags)s" "LIBS=%(libs)s" CPPFLAGS= LDFLAGS= INCLUDES= 
''', locals ())

        targetbuild.TargetBuild.compile (self)
        
    def install (self):
        targetbuild.TargetBuild.install (self)
        self.dump ('''set FONTCONFIG_FILE=$INSTALLER_PREFIX/etc/fonts/fonts.conf
set FONTCONFIG_PATH=$INSTALLER_PREFIX/etc/fonts
''', 
             '%(install_prefix)s/etc/relocate/fontconfig.reloc')
        
        
class Fontconfig__mingw (Fontconfig):
    def patch (self):
        self.apply_patch ('fontconfig-2.6.0-fcstat.patch')
#        self.apply_patch ('fontconfig-2.5.91-public_ft_files.patch')
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
    def configure_command (self):
        cmd = Fontconfig.configure_command (self)
        cmd += ' --with-add-fonts=/Library/Fonts,/System/Library/Fonts '
        return cmd

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

class Fontconfig__tools (toolsbuild.ToolsBuild):
    # FIXME: use mi to get to source?
    source = 'git://anongit.freedesktop.org/git/fontconfig?revision=' + version
    
    def get_build_dependencies (self):
        return ['libtool', 'freetype', 'expat']

    def compile_command (self):
        return (toolsbuild.ToolsBuild.compile_command (self)
                + ' DOCSRC="" ')

    def install_command (self):
        return (toolsbuild.ToolsBuild.install_command (self)
                + ' DOCSRC="" ')

class Fontconfig__cygwin (Fontconfig):
    source = mirrors.with_template (name='fontconfig', mirror=mirrors.fontconfig, version='2.4.1')
    def __init__ (self, settings, source):
        Fontconfig.__init__ (self, settings, source)
        self.so_version = '1'

    def get_subpackage_definitions (self):
        d = dict (Fontconfig.get_subpackage_definitions (self))
        # urg, must remove usr/share. Because there is no doc package,
        # runtime iso '' otherwise gets all docs.
        d['runtime'] = [self.settings.prefix_dir + '/lib']
        return d

    def get_subpackage_names (self):
        #return ['devel', 'doc', '']
        return ['devel', 'runtime', '']

    def get_build_dependencies (self):
        return ['libtool', 'libfreetype2-devel', 'expat']
        #return ['libtool', 'freetype2', 'expat']
    
    def get_dependency_dict (self):
        return {
            '': ['libfontconfig1'],
            'devel': ['libfontconfig1', 'libfreetype2-devel'],
            'runtime': ['expat', 'libfreetype26', 'zlib'],
            }

    def category_dict (self):
        return {'': 'Libs'}

    def configure_command (self):
        return (Fontconfig.configure_command (self)
                + ' --sysconfdir=/etc --localstatedir=/var')

    def install (self):
        self.pre_install_smurf_exe ()
        Fontconfig.install (self)
        name = 'fontconfig-postinstall.sh'
        postinstall = '''#! /bin/sh
# cleanup silly symlink of previous packages
rm -f /usr/X11R6/bin/fontconfig-config
'''
        self.dump (postinstall,
                   '%(install_root)s/etc/postinstall/%(name)s',
                   env=locals ())
