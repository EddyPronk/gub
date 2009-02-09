from gub import target

class Pangomm (target.AutoBuild):
    source = 'http://ftp.acc.umu.se/pub/GNOME/sources/pangomm/2.14/pangomm-2.14.1.tar.gz'
    def _get_build_dependencies (self):
        return ['glibmm-devel', 'libsig++-devel', 'pangocairo-devel']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' CFLAGS=-I%(system_prefix)s/include/freetype2'
                + ''' LDFLAGS='-lfreetype -lz' ''')
    def makeflags (self):
        return ''' 'sublib_cflags=$(PANGOMM_CFLAGS) $(CFLAGS)' '''
