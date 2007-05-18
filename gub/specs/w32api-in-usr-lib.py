from gub import gubb

class W32api_in_usr_lib (gubb.BinarySpec, gubb.SdkBuildSpec):
    def __init__ (self, settings):
        gubb.BinarySpec.__init__ (self, settings)
        self.with_template (version='1.0',  strip_components=0)
    def get_build_dependencies (self):
        return ['w32api']
    def install (self):
        self.system ('mkdir -p %(install_root)s/usr/lib')
        self.system ('''
tar -C %(system_root)s/usr/lib/w32api -cf- . | tar -C %(install_root)s/usr/lib -xf-
''')

