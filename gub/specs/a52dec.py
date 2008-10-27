from gub import targetbuild

a52 = 'http://liba52.sourceforge.net/files/%(name)s-%(ball_version)s.tar.%(format)s'

class A52dec (targetbuild.AutoBuild):
    source = mirrors.with_tarball (name='a52dec', mirror=a52, version='0.7.4')
    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                + ' CFLAGS=-fPIC')
        
