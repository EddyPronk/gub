import download
import gub

class Osx_lilypad (gub.NullBuildSpec):
    def __init__ (self, settings):
        gub.NullBuildSpec.__init__ (self, settings)
        self.with (version="0.2", mirror=download.hw)
