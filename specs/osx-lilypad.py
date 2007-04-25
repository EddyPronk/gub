import mirrors
import gub

class Osx_lilypad (gub.NullBuildSpec):
    pass

class Osx_lilypad__darwin__ppc (gub.NullBuildSpec):
    def __init__ (self, settings):
        gub.NullBuildSpec.__init__ (self, settings)
        self.with (version="0.2",
                   mirror='http://lilypond.org/download/gub-sources/osx-lilypad-ppc-0.2.tar.gz')

class Osx_lilypad__darwin__x86 (gub.NullBuildSpec):
    def __init__ (self, settings):
        gub.NullBuildSpec.__init__ (self, settings)
        self.with (version="0.2",
                   mirror='http://lilypond.org/download/gub-sources/osx-lilypad-x86-0.2.tar.gz')
