from gub import build

class W32api_in_usr_lib (build.BinaryBuild, build.SdkBuild):
    source = 'url://host/w32api-in-usr-lib-1.0.tar.gz'
    def _get_build_dependencies (self):
        return ['w32api']
    def install (self):
        self.system ('mkdir -p %(install_prefix)s/lib')
        self.system ('''
tar -C %(system_prefix)s/lib/w32api -cf- . | tar -C %(install_prefix)s/lib -xf-
''')

