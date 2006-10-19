import download
import gub
import misc
import targetpackage
import toolpackage

class Fontconfig (targetpackage.TargetBuildSpec):
    '''Generic font configuration library - %(flavor)s
Fontconfig is a font configuration and customization library, which
does not depend on the X Window System.  It is designed to locate
fonts within the system and select them according to requirements
specified by applications.'''

    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
#        self.with (mirror="git://anongit.freedesktop.org/git/fontconfig", version="master", vc_type='git')
        self.with (mirror=download.fontconfig,
                   version="2.4.1")
        
    def get_build_dependencies (self):
        return ['libtool', 'expat-devel', 'freetype-devel']

    def get_dependency_dict (self):
        return {'': ['expat', 'freetype', 'libtool']}

    def configure_command (self):
        # FIXME: system dir vs packaging install

        ## UGH  - this breaks  on Darwin!
        return (targetpackage.TargetBuildSpec.configure_command (self) 
                + misc.join_lines ('''
--with-arch=%(target_architecture)s
--with-freetype-config="%(system_root)s/usr/bin/freetype-config
--prefix=%(system_root)s/usr
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

        cflags = '-I%(srcdir)s -I%(srcdir)s/src ' \
            + self.read_pipe ('freetype-config --cflags')[:-1]
        libs = self.read_pipe ('freetype-config --libs')[:-1]
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
             '%(install_root)s/usr/etc/relocate/fontconfig.reloc')
        
        
class Fontconfig__mingw (Fontconfig):
    def patch (self):
        Fontconfig.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 < %(patchdir)s/fontconfig-2.4.1-mingw.patch')
        self.system ('cd %(srcdir)s && python %(patchdir)s/fontconfig-make-def.py doc/*.fncs > src/fontconfig.def.in')

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
            'sys_lib_search_path_spec="%(system_root)s/usr/lib /lib '),
            # FIXME: typo: dl_search (only dlsearch exists).
            # comment-out for now
            #('^sys_lib_dl_search_path_spec="/lib/* ',
            # 'sys_lib_dl_search_path_spec="%(system_root)s/usr/lib /lib ')
            ],
               '%(builddir)s/libtool')

class Fontconfig__freebsd (Fontconfig__linux):
    pass

class Fontconfig__local (toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with (version='2.4.1', mirror=download.fontconfig)
        
    def get_build_dependencies (self):
        return ['libtool', 'freetype', 'expat']

    def compile_command (self):
        return  toolpackage.ToolBuildSpec.compile_command (self) + ' DOCSRC="" '   
    def install_command (self):
        return  toolpackage.ToolBuildSpec.install_command (self) + ' DOCSRC="" '   
class Fontconfig__cygwin (Fontconfig):
    def get_subpackage_names (self):
        #return ['devel', 'doc', '']
        return ['devel', 'runtime', '']

    def get_subpackage_definitions (self):
        d = dict (Fontconfig.get_subpackage_definitions (self))
        # FIXME: we do this for all cygwin packages
        d['runtime'].append ('/usr/bin/cyg*dll')
        return d

    def get_build_dependencies (self):
        return ['libtool', 'libfreetype2-devel', 'expat']
    
    def get_dependency_dict (self):
        return {
            '': ['libfontconfig1'],
            'devel': ['libfontconfig1', 'libfreetype2-devel'],
            'runtime': ['expat', 'libfreetype26', 'zlib'],
            }

    def category_dict (self):
        return {'': 'libs',
                'runtime': 'libs',
                'devel': 'devel libs',
                'doc': 'doc'}

    def description_dict (self):
        # FIXME: fairly uninformative description for packages,
        # unlike, eg, guile-devel.  This is easier, though.
        d = {}
        for i in self.get_subpackage_names ():
            d[i] = self.get_subpackage_doc (i)
        return d

    def get_subpackage_doc (self, split):
        flavor = {'': 'executables',
                  'devel': 'development',
                  'doc': 'documentation',
                  'runtime': 'runtime'}[split]
        return Fontconfig.__doc__ % locals ()

    def configure_command (self):
        return (Fontconfig.configure_command (self)
                + ' --sysconfdir=/etc --localstatedir=/var')

    def install (self):
        Fontconfig.install (self)
        # FIXME: we do this for all cygwin packages
	self.post_install_smurf_exe ()
        self.install_readmes ()
        
    
