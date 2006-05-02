from toolpackage import Tool_package
import download

class Pkg_config (Tool_package):
    def __init__ (self, settings):
        Tool_package.__init__ (self, settings)
        self.with (version="0.20",
             mirror=download.freedesktop),
