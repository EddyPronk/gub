from gub import mirrors
from gub import targetbuild

class Regex (targetbuild.TargetBuild):
    def __init__ (self, settings, source):
        targetbuild.TargetBuild.__init__ (self, settings, source)
        self.with_template (version='2.3.90-1',
                   mirror=mirrors.lilypondorg, format='bz2')
