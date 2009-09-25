import os
import sys
#
from gub import misc
from gub import repository
from gub.specs import guile
from gub.specs import lilypond

# FIXME: make target.Installer/target.BaseBuild packag?
# This is much more work than just calling
#   bin/gib --platform= --branch=PACKAGE=BRANCH PACKAGE
# not really a 'python driver'.
class LilyPond_installer (lilypond.LilyPond_base):
    dependencies = [self.settings.target_platform + '::lilypond']
    def compile (self):
        self.system (self.compile_command ())
    def compile_command (self):
        # FIXME: ugh, no branches anymore in self.settings.branches['guile'],
        # let's hope/assume the user did not override guile source or branch...
        dir = os.path.join (self.settings.downloads, 'guile')
        guile_branch = repository.get_repository_proxy (dir, guile.Guile.source, guile.Guile.branch).full_branch_name ()
        #guile_branch = guile.Guile (self.settings, guile.Guile.source).source.full_branch_name ()
        lilypond_branch = self.source.full_branch_name ()
        return (sys.executable
                + misc.join_lines ('''
bin/gib
--platform=%%(target_platform)s
--branch=guile=%(guile_branch)s
--branch=lilypond=%(lilypond_branch)s
lilypond
''' % locals ()))
    def install_command (self):
        return 'true'

class LilyPond_installer__mingw (LilyPond_installer):
    dependencies = (LilyPond_installer.dependencies
                    + ['lilypad', 'tools::icoutils', 'tools::nsis'])
    compile_flags = LilyPond_installer.compile_flags + ' lilypad'

Lilypond_installer = LilyPond_installer
Lilypond_installer__mingw = LilyPond_installer__mingw
