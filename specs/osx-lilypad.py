import download
import gub

class Osx_lilypad (gub.Null_package):
    def __init__ (self, settings):
        gub.Null_package.__init__ (self, settings)
        self.with (version="0.2", mirror=download.hw, builddeps=[])
