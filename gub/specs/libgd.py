from gub import target
from gub import tools

class Libgd (target.AutoBuild):
    source = 'http://www.libgd.org/releases/gd-2.0.36RC1.tar.gz'
    dependencies = [
            'tools::libtool',
            'fontconfig',
            'freetype',
            'libjpeg',
            'libpng',
            'zlib',
            ]
    configure_flags = (target.AutoBuild.configure_flags
                + ' --with-fontconfig'
                + ' --with-freetype'
                + ' --with-jpeg'
                + ' --with-png'
                + ' --without-xpm'
                )

class Libgd__tools (tools.AutoBuild, Libgd):
    dependencies = [
            'fontconfig',
            'freetype',
            'libjpeg',
            'libpng',
            'libtool',
            'zlib',
            ]
    configure_flags = (tools.AutoBuild.configure_flags
                + ' --with-fontconfig'
                + ' --with-freetype'
                + ' --with-jpeg'
                + ' --with-png'
                + ' --without-xpm'
                )
