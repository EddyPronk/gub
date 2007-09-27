from gub import mirrors
from gub import gubb
from gub import misc
from gub import targetpackage
from gub import toolpackage
from gub import repository

fc_version = "0596d7296c94b2bb9817338b8c1a76da91673fb9"

class Fontconfig (targetpackage.TargetBuildSpec):
    '''Generic font configuration library 
Fontconfig is a font configuration and customization library, which
does not depend on the X Window System.  It is designed to locate
fonts within the system and select them according to requirements
specified by applications.'''

    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_vc (repository.Git (self.get_repodir (),
                                      source="git://anongit.freedesktop.org/git/fontconfig",
                                      revision=fc_version))
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

        return (targetpackage.TargetBuildSpec.configure_command (self) 
                + misc.join_lines ('''
--with-arch=%(target_architecture)s
--with-freetype-config="%(system_prefix)s/cross/bin/freetype-config
--prefix=%(system_prefix)s
"'''))

    def configure (self):
        self.system ('''
rm -f %(srcdir)s/builds/unix/{unix-def.mk,unix-cc.mk,ftconfig.h,freetype-config,freetype2.pc,config.status,config.log}
''')
        targetpackage.TargetBuildSpec.configure (self)

        ## FIXME: libtool too old for cross compile
        self.update_libtool ()
        self.file_sub ([('DOCSRC *=.*', 'DOCSRC=')],
                       '%(builddir)s/Makefile')

    def compile (self):

        # help fontconfig cross compiling a bit, all CC/LD
        # flags are wrong, set to the target's root

        ## we want native freetype-config flags here. 
        cflags = '-I%(srcdir)s -I%(srcdir)s/src ' \
                 + self.read_pipe ('%(local_prefix)s/bin/freetype-config --cflags')[:-1]

        libs = self.read_pipe ('%(local_prefix)s/bin/freetype-config --libs')[:-1]
        for i in ('fc-case', 'fc-lang', 'fc-glyphname', 'fc-arch'):
            self.system ('''
cd %(builddir)s/%(i)s && make "CFLAGS=%(cflags)s" "LIBS=%(libs)s" CPPFLAGS= LDFLAGS= INCLUDES= 
''', locals ())

        targetpackage.TargetBuildSpec.compile (self)
        
    def install (self):
        targetpackage.TargetBuildSpec.install (self)
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

class Fontconfig__local (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with_template (mirror="git://anongit.freedesktop.org/git/fontconfig",
                   version=fc_version)
        
    def get_build_dependencies (self):
        return ['libtool', 'freetype', 'expat']

    def compile_command (self):
        return (toolpackage.ToolBuildSpec.compile_command (self)
                + ' DOCSRC="" ')

    def install_command (self):
        return (toolpackage.ToolBuildSpec.install_command (self)
                + ' DOCSRC="" ')

class Fontconfig__cygwin (Fontconfig):
    def __init__ (self, settings):
        Fontconfig.__init__ (self, settings)
        self.with_template (mirror=mirrors.fontconfig, version='2.4.1')
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
        return {'': 'libs'}

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
