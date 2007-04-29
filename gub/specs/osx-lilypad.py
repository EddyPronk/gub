from gub import mirrors
from gub import gubb

class Osx_lilypad (gubb.NullBuildSpec):
    pass

class Osx_lilypad__darwin__ppc (gubb.NullBuildSpec):
    def __init__ (self, settings):
        gubb.NullBuildSpec.__init__ (self, settings)
        self.with (version="0.2",
                   mirror='http://lilypond.org/download/gub-sources/osx-lilypad-ppc-0.2.tar.gz')

class Osx_lilypad__darwin__x86 (gubb.NullBuildSpec):
    def __init__ (self, settings):
        gubb.NullBuildSpec.__init__ (self, settings)
        self.with (version="0.2",
                   mirror='http://lilypond.org/download/gub-sources/osx-lilypad-x86-0.2.tar.gz')
