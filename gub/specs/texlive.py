import os
#
from gub.syntax import printf
from gub import context
from gub import logging
from gub import loggedos
from gub import misc
from gub import octal
from gub import repository
from gub import target
from gub import tools

# last tested:
# &revision=14796

texlive_svn = 'svn://tug.org/texlive'
license_url = 'http://tug.org/svn/texlive/trunk/Master/LICENSE.TL'

# get the whole /usr/share/texmf-dist too?
# FIXME: resurrect texmf-minimal from old build scripts in simple tar ball
texmf_dist = True

class Texlive (target.AutoBuild):
    '''The TeX Live text formatting system
The TeX Live software distribution offers a complete TeX system.
It  encompasses programs for editing, typesetting, previewing and printing
of TeX documents in many different languages, and a large collection
of TeX macros and font libraries.

The distribution also includes extensive general documentation about
TeX, as well as the documentation accompanying the included software
packages.'''

#    source = texlive_svn + '&branch=trunk&branchmodule=Build/source&revision=HEAD'
    source = 'http://lilypond.org/download/gub-sources/texlive/texlive-15644.tar.gz'
    config_cache_flag_broken = True
    parallel_build_broken = True
    dependencies = [
            'tools::automake',
            'tools::texlive',
            'tools::t1utils',
            'tools::rsync',
            'libtool',
#?            'fontconfig',
            'freetype',
            'libgd',
            'libpng',
            'libtiff',
            'libt1',
            'ncurses',
            'zlib',
            ]
##--with-system-kpathsea
    common_configure_flags = misc.join_lines ('''
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
    LDFLAGS='-L%(system_prefix)s/lib %(rpath)s %(libs)s'
    # PROMOTEME: LDFLAGS should be set in target.py just like tools.py?
    configure_variables = (target.AutoBuild.configure_variables
                           + ''' LDFLAGS='%(rpath)s %(libs)s' ''')
#    configure_command = ('export TEXMF=%(tools_prefix)s/share/texmf;'
#                         + target.AutoBuild.configure_command)
    configure_flags = (target.AutoBuild.configure_flags
                       + '%(common_configure_flags)s'
                       + misc.join_lines ('''
--with-x
--with-mf-x-toolkit=xaw
--with-xdvi-x-toolkit=xaw
--x-includes=%(system_prefix)s/X11R6/include
--x-libraries=%(system_prefix)s/X11R6/lib
'''))
    configure_flags = (target.AutoBuild.configure_flags
                       + (common_configure_flags
                          .replace ('--with-mf-x-toolkit=xaw', '')
                          .replace ('--with-xdvi-x-toolkit=xaw', ''))
                       + ' CPPFLAGS=-I%(system_prefix)s/include'
                       + ' --x-includes='
                       + ' --x-libraries='
                       + ' --disable-xdvik'
                       + ' --disable-xdvipdfmx'
                       + ' --disable-mf'
                       + ' --disable-pdfopen')
#    destdir_install_broken = True
    make_flags = ' SHELL=/bin/bash' # web2c forces `/bin/sh libtool', use bash
    common_install_flags = (
        ''' 'btdocdir=$(datadir)/texmf/doc/bibtex8' '''
        + ''' 'cmapdatadir=$(datadir)/texmf/fonts/cmap/dvipdfmx' '''
        + ''' 'configdatadir=$(datadir)/texmf/dvipdfmx' '''
        + ''' 'csfdir=$(datadir)/texmf-dist/bibtex/csf/base' '''
        + ''' 'encdir=$(datadir)/texmf-dist/fonts/enc/dvips/base' '''
        + ''' 'glyphlistdatadir=$(datadir)/texmf-dist/fonts/map/glyphlist' '''
        + ''' 'glyphlistdir=$(datadir)/texmf-dist/fonts/map/glyphlist' '''
        + ''' 'gsftopkpsheaderdir=$(datadir)/texmf/dvips/gsftopk' '''
        + ''' 'infodir=$(datadir)/info' '''
        + ''' 'mandir=$(datadir)/man' '''
        + ''' 'mapdatadir=$(datadir)/texmf/fonts/map/dvipdfm/dvipdfmx' '''
        + ''' 'prologdir=$(datadir)/texmf/dvips/base' '''
        + ''' 'scriptdir=$(datadir)/texmf-dist/scripts' '''
        + ''' 'scriptxdir=$(datadir)/texmf/scripts' '''
        + ''' 'tetexdocdir=$(datadir)/texmf/doc/tetex' '''
        + ''' 'tex4htdir=$(datadir)/$(tex4ht_subdir)' '''
        + ''' 'texconfigdir=$(datadir)/texmf/texconfig' '''
        + ''' 'web2cdir=$(datadir)/texmf/web2c' '''
        )
    install_flags = (tools.AutoBuild.install_flags
                     + common_install_flags
                     )
    license_files = ['%(srcdir)s/LICENSE.TL']
    ##subpackage_names = ['doc', 'devel', 'base', 'runtime', 'bin', '']
    subpackage_names = ['']

    def init_repos (self):
        if isinstance (self.source, repository.Subversion):
            def fixed_version (self):
                return '2009'
            self.source.version = misc.bind_method (fixed_version, self.source)
            self.texmf_repo = repository.Subversion (
                dir=self.get_repodir () + '-texmf',
                source=texlive_svn,
                branch='trunk',
                branchmodule='Master/texmf',
                revision='HEAD')
            self.texmf_dist_repo = repository.Subversion (
                dir=self.get_repodir () + '-texmf-dist',
                source=texlive_svn,
                branch='trunk',
                branchmodule='Master/texmf-dist',
                revision='HEAD')
        else:
            self.texmf_repo = repository.get_repository_proxy (self.get_repodir ().replace ('texlive', 'texlive-texmf-tiny'),
                                                               Texlive.source.replace ('texlive', 'texlive-texmf-tiny'))
            self.texmf_dist_repo = repository.get_repository_proxy (self.get_repodir ().replace ('texlive', 'texlive-texmf-dist-tiny'),
                                                               Texlive.source.replace ('texlive', 'texlive-texmf-dist-tiny'))

    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        self.init_repos ()
    if 'stat' in misc.librestrict ():
        def LD_PRELOAD (self):
            return '%(tools_prefix)s/lib/librestrict-open.so'
    def version (self):
        return '2009'
    def get_subpackage_definitions (self):
        d = target.AutoBuild.get_subpackage_definitions (self)
        d['doc'] += [self.settings.prefix_dir + '/share/texmf/doc']
        d['doc'] += [self.settings.prefix_dir + '/share/texmf-dist/doc']
        d['base'] = [self.settings.prefix_dir + '/share/texmf']
        d['base'] = [self.settings.prefix_dir + '/share/texmf-dist']
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
    def untar (self):
        target.AutoBuild.untar (self)
        def defer (logger):
            self.texmf_repo.update_workdir (self.expand ('%(srcdir)s/texmf'))
            if texmf_dist:                self.texmf_dist_repo.update_workdir (self.expand ('%(srcdir)s/texmf-dist'))
            # ugh.
            if self.source.have_client ():
                loggedos.download_url (logging.default_logger,
                                       license_url,
                                       self.expand ('%(srcdir)s'))
        self.func (defer)
    def common_patch (self):
        self.file_sub ([(' REL=[.][.] ', ' REL=../share'),],
                       '%(srcdir)s/texk/texlive/linked_scripts/Makefile.in')
        self.file_sub ([
#                ('[{]/share', '{%(prefix_dir)s/share'),
                (' [$]SELFAUTOPARENT/texmf-var', ' $SELFAUTOPARENT/var/lib/texmf'),
                (' [$]SELFAUTOPARENT/texmf-config', ' $SELFAUTODIR/etc/texmf'),
                (' [$]SELFAUTOPARENT/texmf-dist', ' $SELFAUTODIR/share/texmf-dist'),
                (' [$]SELFAUTOPARENT/texmf', ' $SELFAUTODIR/share/texmf'),
                ],
                       '%(srcdir)s/texk/kpathsea/texmf.cnf')
    def patch (self):
        target.AutoBuild.patch (self)
        self.common_patch ()
    def common_install (self):
        self.system ('''
mkdir -p %(install_prefix)s/share/
(cd %(install_prefix)s && tar -cf- texmf* | tar -C share -xf-)
rm -rf %(install_prefix)s/texmf*
rsync -v -a %(srcdir)s/texmf %(install_prefix)s/share/
rsync -v -a %(srcdir)s/texmf-dist %(install_prefix)s/share/ || :
(cd %(install_prefix)s/bin && ln -s pdftex latex)
(cd %(install_prefix)s/bin && ln -s pdftex pdflatex)
rm -f %(install_prefix)s/bin/man
''')
        self.dump ('''#! /bin/sh
texconfig-sys rehash
texconfig-sys confall
texconfig-sys rehash
texconfig-sys init
texconfig-sys dvips printcmd -
''',
                   '%(install_prefix)s/etc/postinstall/texlive',
                   permissions=octal.o755)
    def install (self):
        target.AutoBuild.install (self)
        self.common_install ()
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
#?            'fontconfig',
            'freetype',
            'libgd',
            'libpng',
            'libt1',
            'libtiff',
            'ncurses',
            'rsync',
            't1utils',
            'zlib',
            ]
    configure_flags = (tools.AutoBuild.configure_flags
                       + Texlive.common_configure_flags
                       + ' --without-x')
    install_flags = (tools.AutoBuild.install_flags
                     + Texlive.common_install_flags
                     )
    def __init__ (self, settings, source):
        tools.AutoBuild.__init__ (self, settings, source)
        Texlive.init_repos (self)
    def patch (self):
        tools.AutoBuild.patch (self)
        Texlive.common_patch (self)
    def install (self):
        tools.AutoBuild.install (self)
        Texlive.common_install (self)

def system (cmd, env={}, ignore_errors=False):
    call_env = os.environ.copy ()
    call_env.update (env)
    for i in cmd.split ('\n'):
        if i:
            loggedos.system (logging.default_logger, i % env, call_env, ignore_errors)

def main ():
    version = '15644'
    logging.default_logger.threshold = '1'
    for texmf in ['texlive-texmf', 'texlive-texmf-dist']:
        system ('''
mkdir -p downloads/%(texmf)s-tiny
LANG= tar -C downloads/%(texmf)s-tiny -xvzf downloads/%(texmf)s/%(texmf)s-%(version)s.tar.gz $(sed -e s/^texmf/%(texmf)s-%(version)s/ sourcefiles/texmf-tiny.list) 1> %(texmf)s.list 2> %(texmf)s.missing || :
cd downloads/%(texmf)s-tiny && mv %(texmf)s-%(version)s %(texmf)s-tiny-%(version)s
tar -C downloads/%(texmf)s-tiny -czf downloads/%(texmf)s-tiny/%(texmf)s-tiny-%(version)s.tar.gz %(texmf)s-tiny-%(version)s
rm -rf downloads/%(texmf)s-tiny/%(texmf)s-tiny-%(version)s
''', locals ())
    system ('''
sed s@.*/@@ sourcefiles/texmf-tiny.list | sort > sourcefiles/tiny.list
sed s@.*/@@ texlive-texmf.list texlive-texmf-dist.list | sort > tiny.list
echo diff -purN sourcefiles/tiny.list tiny.list
''')

if __name__ =='__main__':
    main ()
