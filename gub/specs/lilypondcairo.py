from gub.specs import lilypond

# FIXME: this is a version of lilypond which uses pangocairo used by
# Denemo We probably do not want to build pango + cairo for standalone
# lilypond packages, because that would also pull libX11 dependencies
# in.  Hmm.

class Lilypondcairo (lilypond.Lilypond):
    source = 'http://lilypond.org/download/source/v2.13/lilypond-2.13.3.tar.gz'
    def _get_build_dependencies (self):
        return [x.replace ('pango', 'pangocairo')
                for x in lilypond.Lilypond._get_build_dependencies (self)]
    def get_conflict_dict (self):
        return {'': ['lilypond']}

class Lilypondcairo__mingw (lilypond.Lilypond__mingw):
    source = Lilypondcairo.source
    def _get_build_dependencies (self):
        return [x.replace ('pango', 'pangocairo')
                for x in lilypond.Lilypond__mingw._get_build_dependencies (self)]
    def get_conflict_dict (self):
        return {'': ['lilypond']}
