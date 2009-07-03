from gub.specs import lilypond

# FIXME: this is a version of lilypond which uses pangocairo used by
# Denemo We probably do not want to build pango + cairo for standalone
# lilypond packages, because that would also pull libX11 dependencies
# in.  Hmm.

class Lilypondcairo (lilypond.Lilypond):
    source = 'http://ftp.acc.umu.se/pub/GNOME/platform/2.25/2.25.5/sources/lilypond-1.22.4.tar.gz'
    def _get_build_dependencies (self):
        return [x.replace ('pango', 'pangocairo')
                for x in lilypond.Lilypond._get_build_dependencies (self)]
    def get_conflict_dict (self):
        return {'': ['lilypond', 'lilypond-devel', 'lilypond-doc'], 'devel': ['lilypond', 'lilypond-devel', 'lilypond-doc'], 'doc': ['lilypond', 'lilypond-devel', 'lilypond-doc'], 'runtime': ['lilypond', 'lilypond-devel', 'lilypond-doc']}

class Lilypondcairo__mingw (lilypond.Lilypond__mingw):
    def _get_build_dependencies (self):
        return [x.replace ('pango', 'pangocairo')
                for x in lilypond.Lilypond__mingw._get_build_dependencies (self)]
    def get_conflict_dict (self):
        return {'': ['lilypond', 'lilypond-devel', 'lilypond-doc'], 'devel': ['lilypond', 'lilypond-devel', 'lilypond-doc'], 'doc': ['lilypond', 'lilypond-devel', 'lilypond-doc'], 'runtime': ['lilypond', 'lilypond-devel', 'lilypond-doc']}
