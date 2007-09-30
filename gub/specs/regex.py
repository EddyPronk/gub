from gub import mirrors
from gub import targetpackage

class Regex (targetpackage.TargetBuild):
    def __init__ (self, settings):
        targetpackage.TargetBuild.__init__ (self, settings)
        self.with_template (version='2.3.90-1',
                   mirror=mirrors.lilypondorg, format='bz2')

    def license_file (self):
        return '%(srcdir)s/COPYING.LIB'
