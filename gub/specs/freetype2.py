from gub import mirrors
from gub.specs import freetype

class Freetype2__cygwin (freetype.Freetype__cygwin):
    def __init__ (self, settings):
        freetype.Freetype__cygwin.__init__ (self, settings)
        self.with_template (version='2.1.10',
                            mirror=mirrors.nongnu_savannah,
                            name='freetype')
