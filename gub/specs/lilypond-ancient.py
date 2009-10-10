from gub.specs import lilypond

#LilyPond = LilyPond__simple
class LilyPond (lilypond.LilyPond__simple):
    source = lilypond.url (version='v1.4')
    dependencies = lilypond.LilyPond__simple.dependencies + [
        'texlive',
        'cross/gcc-2.95',
        ]
    # got no autoconf-2.13
    #force_autoupdate = True
    make_flags = (lilypond.LilyPond__simple.make_flags
                  + ' builddir=%(builddir)s'
                  + ' config=%(builddir)s/config.make')
    def LD_PRELOAD (self):
        return ''
    def patch (self):
        lilypond.LilyPond__simple.patch (self)
        # These /are/ needed, but something breaks wrt version/name
        # getting.
        self.file_sub ([
                ('eval "REQUIRED"=', 'eval "OPTIONAL"='),
                ('(^STEPMAKE_GCC\()REQUIRED', r'\1OPTIONAL'),
                ('(^STEPMAKE_CXX\()REQUIRED', r'\1OPTIONAL'),
                ('(^STEPMAKE_GXX\()REQUIRED', r'\1OPTIONAL'),
                ('(^STEPMAKE_BISON\()REQUIRED', r'\1OPTIONAL'),
                #], '%(srcdir)s/configure.in')
                ], '%(srcdir)s/configure')
        def defer (logger):
            loggedos.system (logger, self.expand ('cd %(srcdir)s && ln -s /home .'))
        self.func (defer)

Lilypond_ancient = LilyPond

