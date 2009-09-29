from gub import cygwin
from gub import gup
from gub import misc
from gub import target
from gub.specs import lilypond

class LilyPond (lilypond.LilyPond):
    subpackage_names = ['doc', '']
    dependencies = gup.gub_to_distro_deps (lilypond.LilyPond.dependencies,
                                           cygwin.gub_to_distro_dict)
    configure_flags = (lilypond.LilyPond.configure_flags
                       .replace ('--enable-relocation', '--disable-relocation'))
    python_lib = '%(system_prefix)s/bin/libpython*.dll'
    LDFLAGS = '-L%(system_prefix)s/lib -L%(system_prefix)s/bin -L%(system_prefix)s/lib/w32api'
    make_flags = (lilypond.LilyPond.make_flags
                  + ' LDFLAGS="%(LDFLAGS)s %(python_lib)s"')
    def __init__ (self, settings, source):
        lilypond.LilyPond.__init__ (self, settings, source)
        self.dependencies += [misc.with_platform ('lilypond-doc',
                                                  self.settings.build_platform)]
                                                  
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
cd %(install_prefix)s && LIBRESTRICT_ALLOW=/ tar -C %(install_prefix)s -jxf %(docball)s
''',
                  locals ())
    def category_dict (self):
        return {'': 'Publishing'}

Lilypond = LilyPond
