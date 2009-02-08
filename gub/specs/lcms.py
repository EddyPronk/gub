from gub import target

class Lcms (target.AutoBuild):
    source = 'http://www.littlecms.com/lcms-1.17.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool']
    def configure (self):
        target.AutoBuild.configure (self)
        self.system ('rm -f %(srcdir)s/include/icc34.h')
