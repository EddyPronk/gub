import download
import targetpackage

class Regex (targetpackage.Target_package):
    def __init__ (self, settings):
        targetpackage.Target_package.__init__ (self, settings)
        self.with (version='2.3.90-1', mirror=download.hw, format='bz2',
                   depends=['mingw-runtime']),
