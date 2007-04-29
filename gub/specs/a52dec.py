from gub import targetpackage

a52 = 'http://liba52.sourceforge.net/files/%(name)s-%(ball_version)s.tar.%(format)s'

class A52dec (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        self.with_tarball (mirror=a52, version='0.7.4')
    def configure_command (self):
        return (targetpackage.TargetBuildSpec.configure_command (self)
                + ' CFLAGS=-fPIC')
        
