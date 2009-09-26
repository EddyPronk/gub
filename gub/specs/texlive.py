#
from gub.syntax import printf
from gub import context
from gub import logging
from gub import loggedos
from gub import misc
from gub import repository
from gub import target
from gub import tools

# last tested:
# &revision=14796

texlive_svn = 'svn://tug.org/texlive'
license_url = 'http://tug.org/svn/texlive/trunk/Master/LICENSE.TL'

# get the whole /usr/share/texmf-dist too?
# FIXME: resurrect texmf-minimal from old build scripts in simple tar ball
texmf_dist = False

class Texlive (target.AutoBuild):
    '''The TeX Live text formatting system
The TeX Live software distribution offers a complete TeX system.
It  encompasses programs for editing, typesetting, previewing and printing
of TeX documents in many different languages, and a large collection
of TeX macros and font libraries.

The distribution also includes extensive general documentation about
TeX, as well as the documentation accompanying the included software
packages.'''

    source = texlive_svn + '&branch=trunk&branchmodule=Build/source&revision=HEAD'
    config_cache_flag_broken = True
    dependencies = [
            'tools::automake',
            'libtool',
#            'fontconfig',
            'freetype',
            'libgd',
            'libpng',
            'libtiff',
            'libt1',
            'tools::t1utils',
            'zlib',
            ]
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        def fixed_version (self):
            return '2009'
        source.version = misc.bind_method (fixed_version, source)

        self.texmf_repo = repository.Subversion (
# FIXME: module should be used in checkout dir name.
            dir=self.get_repodir () + '-texmf',
#            dir=self.get_repodir () + 'source._checkout_dir (),
            source=texlive_svn,
            branch='trunk',
            branchmodule='Master/texmf',
            revision='HEAD')

        self.texmf_dist_repo = repository.Subversion (
# FIXME: module should be used in checkout dir name.
            dir=self.get_repodir () + '-texmf-dist',
#            dir=self.get_repodir () + 'source._checkout_dir (),
            source=texlive_svn,
            branch='trunk',
            branchmodule='Master/texmf-dist',
            revision='HEAD')
    def version (self):
        return '2009'
    subpackage_names = ['doc', 'devel', 'base', 'runtime', 'bin', '']
    def get_subpackage_definitions (self):
        d = target.AutoBuild.get_subpackage_definitions (self)
        d['doc'] += [self.settings.prefix_dir + '/share/texmf/doc']
        d['base'] = [self.settings.prefix_dir + '/share/texmf']
#        d['bin'] = ['/']
        d['bin'] = ['/etc', self.settings.prefix_dir]
        return d
    def connect_command_runner (self, runner):
        printf ('FIXME: deferred workaround: should support multiple sources')
        if (runner):
            self.texmf_repo.connect_logger (runner.logger)
            self.texmf_dist_repo.connect_logger (runner.logger)
        return target.AutoBuild.connect_command_runner (self, runner)
    def download (self):
        target.AutoBuild.download (self)
        self.texmf_repo.download ()
        if texmf_dist:
            self.texmf_dist_repo.download ()
        # ugh.
        if self.source.have_client ():
            loggedos.download_url (logging.default_logger,
                                   license_url, self.source._checkout_dir ())
    def untar (self):
        target.AutoBuild.untar (self)
        def defer (logger):
            self.texmf_repo.update_workdir (self.expand ('%(srcdir)s/texmf'))
            if texmf_dist:
                self.texmf_dist_repo.update_workdir (self.expand ('%(srcdir)s/texmf-dist'))
        self.func (defer)
    def common_configure_flags (self):
##--with-system-kpathsea
        return misc.join_lines ('''
--disable-cjkutils
--disable-dvi2tty
--disable-dvipdfmx
--disable-dvipng
--disable-lcdf-typetools
--disable-multiplatform
--disable-native-texlive-build
--disable-psutils
--disable-t1utils
--disable-texinfo
--disable-xdvipdfmx
--disable-xetex
--enable-ipc
--enable-omega
--enable-oxdvik
--enable-pdflatex
--enable-pdftex
--enable-shared
--enable-web2c
--with-dialog
--with-etex
--with-freetype2-include=%(system_prefix)s/include/freetype2
--with-pnglib-include=%(system_prefix)s/include/libpng12
--with-system-freetype2
--with-system-gd
--with-system-ncurses
--with-system-pnglib
--with-system-t1lib
--with-system-tifflib
--with-system-zlib
--without-freetype
--without-icu
--without-sam2p
--without-system-freetype
--without-texi2html
--without-ttf2pk
--without-xdvipdfmx
--without-xetex
''')
    configure_command = ('export TEXMFMAIN=%(srcdir)s/texmf;'
                target.AutoBuild.configure_command)
    configure_flags = (target.AutoBuild.configure_flags
                       + '%(common_configure_flags)s'
                       + misc.join_lines ('''
--with-x
--with-mf-x-toolkit=xaw
--with-xdvi-x-toolkit=xaw
--x-includes=%(system_prefix)s/X11R6/include
--x-libraries=%(system_prefix)s/X11R6/lib
'''))
    destdir_install_broken = True
    def install (self):
        target.AutoBuild.install (self)
        self.system ('''
rsync -v -a %(srcdir)s/texmf %(install_prefix)s/share/
rsync -v -a %(srcdir)s/texmf-dist %(install_prefix)s/share/ || :
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

class Texlive__tools (tools.AutoBuild, Texlive):
    dependencies = [
            'automake',
            'libtool',
#            'fontconfig',
            'freetype',
            'libgd',
            'libpng',
            'libt1',
            'libtiff',
            't1utils',
            'zlib',
            ]
    configure_flags = (tools.AutoBuild.configure_flags
                       + Texlive.common_configure_flags
                       + ' --without-x')
    def install (self):
        tools.AutoBuild.install (self)
        self.system ('''
rsync -v -a %(srcdir)s/texmf %(install_prefix)s/share/
rsync -v -a %(srcdir)s/texmf-dist %(install_prefix)s/share/ || :
''')
