from gub import misc
from gub import target

class Xerces_c (target.AutoBuild):
    source = 'http://www.apache.org/dist/xerces/c/2/sources/xerces-c-src_2_8_0.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::autoconf']
    def __init__ (self, settings, source):
        target.AutoBuild.__init__ (self, settings, source)
        self.compile_dict = {
            'XERCESCROOT': '%(builddir)s',
            'TRANSCODER': 'NATIVE',
            'MESSAGELOADER': 'INMEM',
            'NETACCESSOR': 'Socket',
            'THREADS': 'pthread',
            'BITSTOBUILD': '32',
            'LIBS': ' -lpthread ',
            'ALLLIBS': "${LIBS}",
            'CFLAGS': ' -DPROJ_XMLPARSER -DPROJ_XMLUTIL -DPROJ_PARSERS -DPROJ_SAX4C -DPROJ_SAX2 -DPROJ_DOM -DPROJ_DEPRECATED_DOM -DPROJ_VALIDATORS -DXML_USE_NATIVE_TRANSCODER -DXML_USE_INMEM_MESSAGELOADER -DXML_USE_PTHREADS -DXML_USE_NETACCESSOR_SOCKET ',
            'CXXFLAGS': ' -DPROJ_XMLPARSER -DPROJ_XMLUTIL -DPROJ_PARSERS -DPROJ_SAX4C -DPROJ_SAX2 -DPROJ_DOM -DPROJ_DEPRECATED_DOM -DPROJ_VALIDATORS -DXML_USE_NATIVE_TRANSCODER -DXML_USE_INMEM_MESSAGELOADER -DXML_USE_PTHREADS -DXML_USE_NETACCESSOR_SOCKET ',
            }
        target.change_target_dict (self, self.compile_dict)
    def force_sequential_build (self):
        return True
    def autodir (self):
        return '%(srcdir)s/src/xercesc'
    def configure_command (self):
        # We really did not understand autotools, so we cd and ENV
        # around it until it breaks.  And see, our webserver is soo
        # cool, it can serve the INSTALL file!  Let's remove it from
        # the tarball!
        return (self.makeflags () + ' '
                + target.AutoBuild.configure_command (self)
                .replace ('--config-cache', '--cache-file=%(builddir)s/config.cache'))
    def makeflags (self):
        s = ''
        for i in list (self.compile_dict.keys ()):
            s += ' ' + i + '="' + self.compile_dict[i] + '"'
        return s
    def compile_command (self):
        return (target.AutoBuild.compile_command (self)
                + self.makeflags ())
    def install_command (self):
        return (target.AutoBuild.install_command (self)
                + self.makeflags ())
    def configure (self):
        self.shadow ()
        self.config_cache ()
        self.system ('cd %(builddir)s/src/xercesc && %(configure_command)s')
    def compile (self):
        self.system ('cd %(builddir)s/src/xercesc && %(compile_command)s')
    def install (self):
        self.system ('cd %(builddir)s/src/xercesc && %(install_command)s')

class Xerces_c__linux__arm__vfp (Xerces_c):
    source = 'http://www.apache.org/dist/xerces/c/2/sources/xerces-c-src_2_6_0.tar.gz'

class Xerces_c__mingw (Xerces_c):
    source = 'http://www.apache.org/dist/xerces/c/2/sources/xerces-c-src_2_8_0.tar.gz'
    def __init__ (self, settings, source):
        Xerces_c.__init__ (self, settings, source)
        self.compile_dict.update ({
            'THREADS' : 'mthreads',
            'LIBS': '',
            })
        target.change_target_dict (self, self.compile_dict)
