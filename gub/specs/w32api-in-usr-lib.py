from gub import build

class W32api_in_usr_lib (build.BinaryBuild, build.SdkBuild):
    source = mirrors.with_template (name='w32api-in-usr-lib', version='1.0',  strip_components=0)
    def __init__ (self, settings, source):
        build.BinaryBuild.__init__ (self, settings, source)
        print 'FIXME:', __file__, ': strip-components'
        source.strip_components = 0
    def get_build_dependencies (self):
        return ['w32api']
    def install (self):
        self.system ('mkdir -p %(install_prefix)s/lib')
        self.system ('''
tar -C %(system_prefix)s/lib/w32api -cf- . | tar -C %(install_prefix)s/lib -xf-
''')

