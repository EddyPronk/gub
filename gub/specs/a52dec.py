from gub import target

class A52dec (target.AutoBuild):
    source = 'http://liba52.sourceforge.net/files/a52dec-0.7.4.tar.gz'
    configure_variables = (target.AutoBuild.configure_variables
                + ' CFLAGS=-fPIC')
        
