from gub import targetbuild

a52 = 'http://liba52.sourceforge.net/files/%(name)s-%(ball_version)s.tar.%(format)s'

class A52dec (targetbuild.TargetBuild):
    def __init__ (self, settings):
        targetbuild.TargetBuild.__init__ (self, settings)
        self.with_tarball (mirror=a52, version='0.7.4')
    def configure_command (self):
        return (targetbuild.TargetBuild.configure_command (self)
                + ' CFLAGS=-fPIC')
        
