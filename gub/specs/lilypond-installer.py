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
    install_command = 'true'
    def __init__ (self, settings, source):
        lilypond.LilyPond_base.__init__ (self, settings, source)
        self.dependencies = [self.settings.target_platform + '::lilypond']
    def compile (self):
        # FIXME: ugh, no branches anymore in self.settings.branches['guile'],
        # let's hope/assume the user did not override guile source or branch...
        #guile_branch = guile.Guile (self.settings, guile.Guile.source).source.full_branch_name ()
        dir = os.path.join (self.settings.downloads, 'guile')
        guile_branch = repository.get_repository_proxy (dir, guile.Guile.source, guile.Guile.branch).full_branch_name ()
        lilypond_branch = self.source.full_branch_name ()
        compile_command = (sys.executable
                + misc.join_lines ('''
bin/gib
--platform=%%(target_platform)s
--branch=guile=%(guile_branch)s
--branch=lilypond=%(lilypond_branch)s
lilypond
''' % locals ()))
        self.system (compile_command)

class LilyPond_installer__mingw (LilyPond_installer):
    dependencies = (LilyPond_installer.dependencies
                    + ['lilypad', 'tools::icoutils', 'tools::nsis'])
    compile_flags = LilyPond_installer.compile_flags + ' lilypad'
    def __init__ (self, settings, source):
        LilyPond_installer.__init__ (self, settings, source)
        # ugh, that's what you get for modifying CLASS variables
        # in a base-class' INSTANCE
        self.dependencies += self.__class__.dependencies

Lilypond_installer = LilyPond_installer
Lilypond_installer__mingw = LilyPond_installer__mingw
