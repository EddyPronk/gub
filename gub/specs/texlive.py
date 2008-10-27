from gub import repository
from gub import targetbuild
from gub import misc


texlive_svn = 'svn://username@tug.org/texlive'
license_url = 'http://tug.org/svn/texlive/trunk/Master/LICENSE.TL'

class Texlive (targetbuild.AutoBuild):
    '''The TeX Live text formatting system
The TeX Live software distribution offers a complete TeX system.
It  encompasses programs for editing, typesetting, previewing and printing
of TeX documents in many different languages, and a large collection
of TeX macros and font libraries.
 
The distribution also includes extensive general documentation about
TeX, as well as the documentation accompanying the included software
packages.'''

    source = mirrors.with_vc (repository.Subversion (None,
                                                     source=texlive_svn,
                                                     branch='trunk',
                                                     module='AutoBuild/source',
                                                     revision='HEAD'))

    def get_build_dependencies (self):
        return ['tools::autoconf', 'tools::automake', 'tools::libtool']

    def __init__ (self, settings, source):
        targetbuild.AutoBuild.__init__ (self, settings, source)
        def fixed_version (self):
            return '2006'
        from new import instancemethod
        source.version = instancemethod (fixed_version, source, type (source))

        self.texmf_repo = repository.Subversion (
# FIXME: module should be used in checkout dir name.            
            dir=self.get_repodir () + '-texmf',
#            dir=self.get_repodir () + 'source._checkout_dir (),
            source=texlive_svn,
            branch='trunk',
            module='Master/texmf',
            revision='HEAD')

        self.texmf_dist_repo = repository.Subversion (
# FIXME: module should be used in checkout dir name.            
            dir=self.get_repodir () + '-texmf-dist',
#            dir=self.get_repodir () + 'source._checkout_dir (),
            source=texlive_svn,
            branch='trunk',
            module='Master/texmf-dist',
            revision='HEAD')

    def version (self):
        return '2006'
    
    def get_subpackage_names (self):
        return ['doc', 'devel', 'base', 'runtime', 'bin', '']

    def get_subpackage_definitions (self):
        d = targetbuild.AutoBuild.get_subpackage_definitions (self)
        d['doc'] += [self.settings.prefix_dir + '/share/texmf/doc']
        d['base'] = [self.settings.prefix_dir + '/share/texmf']
#        d['bin'] = ['/']
        d['bin'] = ['/etc', self.settings.prefix_dir]
        return d

    def download (self):
        targetbuild.AutoBuild.download (self)
        self.texmf_repo.download ()
        # ugh.
        loggedos.download_url (logging.default_logger,
                               license_url,  self.source._checkout_dir ())
                           
    def untar (self):
        targetbuild.AutoBuild.untar (self)
#        self.texmf_repo.update_workdir (self.expand ('%(srcdir)s/texmf-dist'))
        self.texmf_repo.update_workdir (self.expand ('%(srcdir)s/texmf'))

    def configure_command (self):
        from gub import misc
        #FIXME
        return ('export TEXMFMAIN=%(srcdir)s/texmf;'
                + 'bash '
                + targetbuild.AutoBuild.configure_command (self).replace ('--config-cache', '--cache-file=config.cache')
                + misc.join_lines ('''
--disable-multiplatform
--enable-ipc
--enable-shared
--with-dialog
--with-etex
--with-omega
--with-oxdvik
--with-pdflatex
--with-pdftex
--with-pnglib-include=%(system_prefix)s/include/libpng12
--with-system-freetype
--with-system-freetype2
--with-freetype2-include=%(system_prefix)s/include/freetype2
--with-system-gd
--with-system-ncurses
--with-system-pnglib
--with-system-t1lib
--with-system-tifflib
--with-system-zlib
--with-x
--with-mf-x-toolkit=xaw
--with-xdvi-x-toolkit=xaw
--without-cjkutils
--without-dvi2tty
--without-dvipdfmx
--without-dvipng
--without-icu
--without-lcdf-typetools
--without-psutils
--without-sam2p
--without-t1utils
--without-texi2html
--without-texinfo
--without-ttf2pk
--without-xetex
--without-xdvipdfmx
--x-includes=%(system_prefix)s/X11R6/include
--x-libraries=%(system_prefix)s/X11R6/lib
'''))

    def install_command (self):
        return self.broken_install_command ()

    def install (self):
    	targetbuild.AutoBuild.install (self)
        self.system ('''
#rsync -v -a %(srcdir)s/texmf-dist/* %(install_prefix)s/share/texmf-dist
rsync -v -a %(srcdir)s/texmf/* %(install_prefix)s/share/texmf/
''')

    def license_files (self):
        return ['%(srcdir)s/LICENSE.TL']

    # FIXME: shared for all vc packages
    def srcdir (self):
        return '%(allsrcdir)s/%(name)s-%(version)s'

    # FIXME: shared for all vc packages
    def builddir (self):
        return '%(targetdir)s/build/%(name)s-%(version)s'

    def name_version (self):
        # whugh
        import os
        if os.path.exists (self.srcdir ()):
            d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
            return 'texlive-%(VERSION)s' % d
        return 'texlive-3.0'

class Texlive__cygwin (Texlive):
    def __init__ (self, settings, source):
        Texlive.__init__ (self, settings, source)

    # FIXME: uses mixed gub/distro dependencies
    def get_dependency_dict (self):
        d = Texlive.get_dependency_dict (self)
        d[''] += ['cygwin']
#        d['devel'] += ['cygwin'] + ['bash']
#        d['runtime'] += ['libjpeg62', 'libpng12', 't1lib', 'zlib']
        d[''] += ['libfreetype26', 'libgd2', 'libjpeg62', 'libncurses7', 'libpng12', 't1lib', 'xorg-x11-bin-dlls', 'xaw3d', 'zlib']
        return d
 
    # FIXME: uses mixed gub/distro dependencies
    def get_build_dependencies (self):
        return ['jpeg', 'libfreetype2-devel', 'libgd-devel', 'libncurses-devel', 'libpng12-devel', 'libtool', 't1lib', 'xorg-x11-devel', 'xaw3d', 'zlib']

    def config_cache_overrides (self, str):
        # split part to Texlive ?
        return (str + '''
xdvi_cv_bitmap_type=${xdvi_cv_bitmap_type='BMTYPE=int BMBYTES=4'}
xdvi_cv_func_poll=${xdvi_cv_func_poll=yes}
xdvi_cv_sys_streams=${xdvi_cv_sys_streams=no}
xdvi_cv_sys_sunos_4=${xdvi_cv_sys_sunos_4=no}
xdvi_cv_motif_include=${xdvi_cv_motif_include=no}
xdvi_cv_motif_libdir=${xdvi_cv_motif_libdir=no}
xdvi_cv_func_good_vsnprintf=${xdvi_cv_func_good_vsnprintf=yes}
ac_cv_func_vfork_works=${ac_cv_func_vfork_works=yes}
xdvi_cv_setsid_in_vfork=${xdvi_cv_setsid_in_vfork=yes}
lt_cv_cc_dll_switch=${lt_cv_cc_dll_switch="-Wl,--dll -nostartfiles"}
''')

    def patch (self):
        # FIXME: duh: cross-compile auto-enables t1lib
        for i in self.locate_files ('%(srcdir)s', 'configure'):
            self.file_sub ([
                    ('ac_compile_t1lib=1', 'ac_compile_t1lib=0'),
                    ('-lpng ', '-lpng12 '),
                    ('-lpng"', '-lpng12"'),
                    ], i)
        self.file_sub ([('^(/\* kpsewhich --)', '#undef KPSE_DLL\n\\1')],
                       '%(srcdir)s/texk/kpathsea/kpsewhich.c')

    def makeflags (self):
        from gub import misc
        return misc.join_lines ('''
CFLAGS="-O2 -g -DKPSE_DLL"
''')

    def compile_command (self):
        return (Texlive.compile_command (self) + self.makeflags ())

    def install (self):
    	self.pre_install_smurf_exe ()
        Texlive.install (self)
        
    # FIXME: we do most of this for all cygwin packages
    def category_dict (self):
        return {'': 'Text Publishing',
                'base': 'Text Publishing',
                'extra': 'Text Publishing',}

    def description_dict (self):
        # FIXME: fairly uninformative description for packages,
        # unlike, eg, guile-devel.  This is easier, though.
        d = {}
        for i in self.get_subpackage_names ():
            d[i] = self.get_subpackage_doc (i)
        return d

    def get_subpackage_doc (self, split):
        flavor = {'': 'installer helper',
                  'bin': 'executables',
                  'base': 'base texmf tree',
                  'extra': 'full texmf tree',
                  'devel': 'development',
                  'doc': 'documentation',
                  'runtime': 'runtime',
                  'x11': 'x11 executables',
                  }[split]
        return (Texlive.__doc__.replace ('\n', ' - %(flavor)s\n', 1)
                % locals ())
