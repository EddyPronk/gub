from gub import target

class Pangomm (target.AutoBuild):
    source = 'http://ftp.acc.umu.se/pub/GNOME/sources/pangomm/2.14/pangomm-2.14.1.tar.gz'
    dependencies = ['cairomm-devel', 'glibmm-devel', 'libsig++-devel', 'pangocairo-devel']
    configure_variables = (target.AutoBuild.configure_variables
                           + ' CFLAGS=-I%(system_prefix)s/include/freetype2'
                           + ''' LDFLAGS='-lfreetype -lz' ''')
    make_flags = ''' 'sublib_cflags=$(PANGOMM_CFLAGS) $(CFLAGS)' '''
