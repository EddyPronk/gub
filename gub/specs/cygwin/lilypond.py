from gub import target
from gub.specs import lilypond

class LilyPond (lilypond.LilyPond):
    subpackage_names = ['doc', '']
    def get_dependency_dict (self): #cygwin
        return {
            '' :
            [
            'glib2',
            'guile-runtime',
            'fontconfig-runtime', ## CYGWIN name: 'libfontconfig1',
            #'freetype2-runtime', ## CYGWIN name: 'libfreetype26',
            'libfreetype26',
            'libiconv2',
            'libintl8', 'libintl3',
            'pango-runtime',
            'python',
            ]
            + [
            'bash',
            'coreutils',
            'cygwin',
            'findutils',
            'ghostscript',
            ],
            'doc': ['texinfo'],
            }
    def get_build_dependencies (self): #cygwin
        #FIXME: aargh, MUST specify bash, coreutils etc here too.
        # If get_dependency_dict () lists any packages not # cygwin
        # part of build_dependencies, we get:

        # Using version number 2.8.6 unknown package bash
        # installing package: bash
        # Traceback (most recent call last):
        #   File "installer-builder.py", line 171, in ?
        #     main ()
        #   File "installer-builder.py", line 163, in main
        #     run_installer_commands (cs, settings, commands)
        #   File "installer-builder.py", line 130, in run_installer_commands
        #     build_installer (installer_obj, args)
        #   File "installer-builder.py", line 110, in build_installer
        #     install_manager.install_package (a)
        #   File "lib/gup.py", line 236, in install_package
        #     d = self._packages[name]
        # KeyError: 'bash'
        return [
            ## FIXME: for distro we don't use get_base_package_name,
            ## so we cannot use split-package names for gub/source
            ## build dependencies

            ##'gettext-devel',
            'flex',
            'tools::autoconf',
            'tools::flex',
            'tools::bison',
            'tools::texinfo',
            'tools::fontforge',
            'tools::pkg-config',
            'tools::gettext', # AM_GNU_GETTEXT
            'tools::t1utils',
            'tools::texi2html',
            #'tools::texlive',
            'system::mf', 
            'system::mpost', 
            ##'guile-devel',
            'guile',
            'python',
            ##'fontconfig', ## CYGWIN: 'libfontconfig-devel',
            'libfontconfig-devel',
            ##'freetype2', ## CYGWIN: 'libfreetype2-devel',
            'libfreetype2-devel',
            # cygwin bug: pango-devel should depend on glib2-devel
            'pango-devel', 'glib2-devel',
            'urw-fonts'] + [
            'bash',
            'coreutils',
            'findutils',
            'ghostscript',
            'lilypond-doc',
            ]
    configure_flags = (lilypond.LilyPond.configure_flags
                       .replace ('--enable-relocation', '--disable-relocation'))
    python_lib = '%(system_prefix)s/bin/libpython*.dll'
    LDFLAGS = '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api'
    make_flags = (lilypond.LilyPond.make_flags
                     + ' LDFLAGS="%(LDFLAGS)s %(python_lib)s"')
    def compile (self):
        # Because of relocation script, python must be built before scripts
        self.system ('''
cd %(builddir)s && make -C python %(compile_flags)s
cd %(builddir)s && make -C scripts %(compile_flags)s
cp -pv %(system_prefix)s/share/gettext/gettext.h %(system_prefix)s/include''')
        lilypond.LilyPond.compile (self)
    def install (self):
        ##lilypond.LilyPond.install (self)
        target.AutoBuild.install (self)
        self.install_doc ()
    def install_doc (self):
        # lilypond.make uses `python gub/versiondb.py --build-for=2.11.32'
        # which only looks at source ball build numbers, which are always `1'
        # This could be fixed, but for now just build one doc ball per release?
        installer_build = '1'
        installer_version = self.build_version ()
        docball = self.expand ('%(uploads)s/lilypond-%(installer_version)s-%(installer_build)s.documentation.tar.bz2', env=locals ())

        self.system ('''
mkdir -p %(install_prefix)s/share/doc/lilypond
tar -C %(install_prefix)s -jxf %(docball)s
''',
                  locals ())
    def category_dict (self):
        return {'': 'Publishing'}

Lilypond = LilyPond
