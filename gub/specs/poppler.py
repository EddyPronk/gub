from gub import target

class Poppler (target.AutoBuild):
    source = 'http://poppler.freedesktop.org/poppler-0.10.3.tar.gz'
    def _get_build_dependencies (self):
        return ['tools::libtool', 'tools::glib', 'zlib-devel', 'fontconfig-devel', 'libjpeg-devel', 'libxml2-devel']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ' --disable-poppler-qt'
                + ' --disable-poppler-qt4'
                + ' --enable-xpdf-headers')
