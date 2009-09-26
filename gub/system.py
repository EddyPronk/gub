
#
from gub import build
from gub import configure
from gub import context
from gub import misc

def change_target_package (package):
    pass

def get_cross_build_dependencies (settings):
    return []

class Configure (build.Build):
    install_after_build = False
    source = 'foo.tar.gz'
    vc_branch_suffix = ''
    srcdir = 'foo'
    configure_prefix = ''
    configure_command = ''
    install_prefix = ''
    install_root = ''
    job_spec = ''
    def __init__ (self, settings, source):
        build.Build.__init__ (self, settings, source)
        self._name, self._version = (self._created_name + '-').split ('-')[:2]
    def download (self):
        pass
    def get_stamp_file (self):
        return self.expand ('%(stamp_file)s')
    def stages (self):
        return ['configure']
    def required (self):
         return configure.required
    def configure (self):
        def check (logger):
            configure.test_program (self.required (), self.name (), self.version (),
                                    self.description (), self.package (),
                                    #logger=self.runner.logger.error
                                    )
        self.func (check)
        check (self.runner.logger)
    def get_packages (self):
        return [self]
    def dict (self):
        return self.get_substitution_dict ()
    def name (self):
        return self._name
    def version (self):
        return self._version
    def description (self):
        return self._name
    def package (self):
        return self._name
    @context.subst_method
    def source_checksum (self):
        return self.name () + '-' + self.version ()
    def get_substitution_dict (self, env={}):
        dict = {
            'source_checksum': self.__class__.__name__,
            'split_ball': '',
            'split_hdr': '',
        }
        dict.update (env)
        d = build.Build.get_substitution_dict (self, dict).copy ()
        return d
    @context.subst_method
    def version (self):
        return ''
