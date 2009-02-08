#
from gub import misc
from gub import target
from gub.specs import lilypond

class LilyPond_doc (target.NullBuild):
#    source = 'url://host/lilypond-doc-1.0.tar.gz'
    source = lilypond.LilyPond.source
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        source.version = misc.bind_method (lilypond.LilyPond.version_from_VERSION, source)
        source.is_tracking = misc.bind_method (lambda x: True, source)
        source.is_downloaded = misc.bind_method (lambda x: True, source)
        source.update_workdir = misc.bind_method (lambda x: True, source)
    def _get_build_dependencies (self):
        return [self.settings.build_platform + '::lilypond',
                'tools::netpbm',
                'tools::imagemagick',
                'tools::rsync', # ugh, we depend on *rsync* !?
                #'tools::texlive',
                ]
    def stages (self):
        return misc.list_insert_before (target.NullBuild.stages (self),
                                        'install',
                                        ['compile'])
    def builddir (self):
        #URWGSGSEWNG
        return '%(allbuilddir)s/lilypond%(ball_suffix)s'
    def srcdir (self):
        #URWGSGSEWNG
        return '%(allsrcdir)s/lilypond%(ball_suffix)s'
    def makeflags (self):
        return misc.join_lines ('''
CROSS=no
DOCUMENTATION=yes
WEB_TARGETS="offline online"
TARGET_PYTHON=/usr/bin/python'
''')
    def compile_command (self):
        return (target.AutoBuild.compile_command (self)
                + ' do-top-doc all doc web')
    def install_command (self):
        return (target.AutoBuild.install_command (self)
                .replace (' install', ' web-install'))
    def install (self):
        target.AutoBuild.install (self)

Lilypond_doc = LilyPond_doc
