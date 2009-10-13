import os
#
from gub import build
from gub import loggedos
from gub.specs import lilypond

#LilyPond = LilyPond__simple
class LilyPond (lilypond.LilyPond__simple):
    source = lilypond.url (version='v1.4')
    dependencies = [x for x in lilypond.LilyPond__simple.dependencies
                    if not x in ['system::mf', 'system::mpost']] + [
        'texlive',
        'cross/gcc-2-95',
        ]
    # got no autoconf-2.13
    # force_autoupdate = True
#    configure_variables = (lilypond.LilyPond__simple.configure_variables
#                           + 'CC=%(cross_prefix)s/
    make_flags = (lilypond.LilyPond__simple.make_flags
                  + ' builddir=%(builddir)s'
                  + ' config=%(builddir)s/config.make')
    def __init__ (self, settings, source):
        lilypond.LilyPond__simple.__init__ (self, settings, source)
        build.change_dict (self, {'PATH': '%(cross_prefix)s-ancient/bin:%(tools_prefix)s/bin:%(tools_cross_prefix)s/bin:' + os.environ['PATH']})
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
            srcdir = self.expand ('%(srcdir)s')
            base = srcdir[:srcdir[1:].find ('/') + 1]
            loggedos.system (logger, self.expand ('cd %%(srcdir)s && ln -s %(base)s .' % locals ()))
        self.func (defer)

Lilypond_ancient = LilyPond

