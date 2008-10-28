from gub import targetbuild

class A52dec (targetbuild.AutoBuild):
    source = 'http://liba52.sourceforge.net/files/a52dec-0.7.4.tar.gz'
    def configure_command (self):
        return (targetbuild.AutoBuild.configure_command (self)
                + ' CFLAGS=-fPIC')
        
