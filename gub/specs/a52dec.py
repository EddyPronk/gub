from gub import target

class A52dec (target.AutoBuild):
    source = 'http://liba52.sourceforge.net/files/a52dec-0.7.4.tar.gz'
    def configure_variables (self):
        return (target.AutoBuild.configure_variables (self)
                + ' CFLAGS=-fPIC')
        
