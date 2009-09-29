from gub.specs import lilypond

# FIXME: this is a version of lilypond which uses pangocairo used by
# Denemo We probably do not want to build pango + cairo for standalone
# lilypond packages, because that would also pull libX11 dependencies
# in.  Hmm.

class Lilypondcairo (lilypond.Lilypond):
    source = 'http://lilypond.org/download/source/v2.13/lilypond-2.13.4.tar.gz'
    dependencies = [x.replace ('pango', 'pangocairo')
                for x in lilypond.Lilypond.dependencies]
    def get_conflict_dict (self):
        return {'': ['lilypond']}

class Lilypondcairo__mingw (lilypond.Lilypond__mingw):
    source = Lilypondcairo.source
    dependencies = [x.replace ('pango', 'pangocairo')
                for x in lilypond.Lilypond__mingw.dependencies]
    def get_conflict_dict (self):
        return {'': ['lilypond']}

class Lilypondcairo__darwin (lilypond.Lilypond__darwin):
    source = Lilypondcairo.source
    dependencies = [x.replace ('pango', 'pangocairo')
                for x in lilypond.Lilypond__darwin
                .dependencies]
    def get_conflict_dict (self):
        return {'': ['lilypond']}

class Lilypondcairo__darwin__ppc (lilypond.Lilypond__darwin__ppc):
    source = Lilypondcairo.source
    dependencies = [x.replace ('pango', 'pangocairo')
                for x in lilypond.Lilypond__darwin__ppc
                .dependencies]
    def get_conflict_dict (self):
        return {'': ['lilypond']}
