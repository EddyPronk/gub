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
        self.system ('mkdir -p %(cross_prefix)s%(prefix_dir)s/bin')
        self.file_sub ([
             ('@PYTHON_VERSION@', self.expand ('%(version)s')),
             ('@PREFIX@', self.expand ('%(system_prefix)s/')),
             ('@PYTHON_FOR_BUILD@', sys.executable)],
            '%(sourcefiledir)s/python-config.py.in',
            to_name='%(install_prefix)s/cross/bin/python-config')
        self.system ('chmod 755 %(install_prefix)s/cross/bin/python-config')

class Python_config__cygwin (Python_config):
    source = repository.Version (name='python-config', version='2.5')
