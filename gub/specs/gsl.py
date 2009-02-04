from gub import target

class Gsl (target.AutoBuild):
    source = 'http://ftp.gnu.org/gnu/gsl/gsl-1.12.tar.gz'
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        # --as-needed breaks; ugh, this does not clean LDFLAGS
        target.change_target_dict (self, {'LD': '', 'LDFLAGS': '' })
    def _get_build_dependencies (self):
        return []
    def configure_command (self):
        return target.AutoBuild.configure_command (self) + ' LDFLAGS= '
