import sys
import re

from gub import build
from gub import misc
from gub import repository

class Python_config (build.SdkBuild):
    source = repository.Version (name='python-config', version='2.4.1')
    def stages (self):
        return misc.list_remove (build.SdkBuild.stages (self),
                       ['download', 'untar', 'patch'])
    # FIXME: c&p python.py:install ()
    def install (self):

        build.SdkBuild.install (self)
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        python_config = self.expand ('%(install_prefix)s%(cross_dir)s/bin/python-config')
        self.file_sub ([
             ('@PYTHON_VERSION@', self.expand ('%(version)s')),
             ('@PREFIX@', self.expand ('%(system_prefix)s/')),
             ('@PYTHON_FOR_BUILD@', sys.executable)],
            '%(sourcefiledir)s/python-config.py.in',
            to_name=python_config)
        self.chmod (python_config, 755)

class Python_config__cygwin (Python_config):
    source = repository.Version (name='python-config', version='2.5')
