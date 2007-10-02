from gub import mirrors
from gub import build

class Osx_lilypad (build.NullBuild):
    pass

class Osx_lilypad__darwin__ppc (build.NullBuild):
    def __init__ (self, settings, source):
        build.NullBuild.__init__ (self, settings, source)
    source = mirrors.with_template (name='osx-lilypad', version="0.2",
                   mirror='http://lilypond.org/download/gub-sources/osx-lilypad-ppc-0.2.tar.gz')

class Osx_lilypad__darwin__x86 (build.NullBuild):
    def __init__ (self, settings, source):
        build.NullBuild.__init__ (self, settings, source)
    source = mirrors.with_template (name='osx-lilypad', version="0.2",
                   mirror='http://lilypond.org/download/gub-sources/osx-lilypad-x86-0.2.tar.gz')
