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
        import re
        build.SdkBuild.install (self)
        self.system ('mkdir -p %(cross_prefix)s%(prefix_dir)s/bin')
        s = self.read_file ('%(sourcefiledir)s/python-config.py.in')
        s = re.sub ('@PYTHON_VERSION@', self.expand ('%(version)s'), s)
        s = re.sub ('@PREFIX@', self.expand ('%(system_prefix)s/'), s)
        import sys
        s = re.sub ('@PYTHON_FOR_BUILD@', sys.executable, s)
        self.dump (s, '%(install_prefix)s/cross/bin/python-config',
                   expand_string=False, permissions=0755)

class Python_config__cygwin (Python_config):
    source = repository.Version (name='python-config', version='2.5')
