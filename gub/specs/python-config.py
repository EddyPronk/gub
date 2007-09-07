from gub import gubb

class Python_config (gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False
        self.with_template (version='2.4.1')
    def untar (self):
        pass
    # FIXME: c&p python.py:install ()
    def install (self):
        import re
        gubb.SdkBuildSpec.install (self)
        self.system ('mkdir -p %(cross_prefix)s%(prefix_dir)s/bin')
        cfg = open (self.expand ('%(sourcefiledir)s/python-config.py.in')).read ()
        cfg = re.sub ('@PYTHON_VERSION@', self.expand ('%(version)s'), cfg)
        cfg = re.sub ('@PREFIX@', self.expand ('%(system_prefix)s/'), cfg)
        import sys
        cfg = re.sub ('@PYTHON_FOR_BUILD@', sys.executable, cfg)
        self.dump (cfg, '%(install_prefix)s/cross/bin/python-config',
                   expand_string=False)
        self.system ('chmod +x %(install_prefix)s/cross/bin/python-config')

class Python_config__cygwin (Python_config):
    def __init__ (self, settings):
        gubb.SdkBuildSpec.__init__ (self, settings)
        self.has_source = False
        self.with_template (version='2.5')
