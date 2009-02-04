from gub import target

class Pangomm (target.AutoBuild):
    source = 'http://ftp.acc.umu.se/pub/GNOME/sources/pangomm/2.14/pangomm-2.14.1.tar.gz'
    def _get_build_dependencies (self):
        return ['pangocairo-devel', 'libsig++-devel']
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
       return {'': [x.replace ('-devel', '')
                    for x in self._get_build_dependencies ()
                    if 'tools::' not in x and 'cross/' not in x]}
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' CFLAGS=-I%(system_prefix)s/include/freetype2'
                + ''' LDFLAGS='-lfreetype -lz' ''')
    def makeflags (self):
        return ''' 'sublib_cflags=$(PANGOMM_CFLAGS) $(CFLAGS)' '''
