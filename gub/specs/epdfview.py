from gub import target

class Epdfview (target.AutoBuild):
    source = 'http://trac.emma-soft.com/epdfview/chrome/site/releases/epdfview-0.1.7.tar.gz'
    dependencies = [
            'tools::automake',
            'tools::gettext',
            'tools::libtool',
            'tools::pkg-config',
            'gtk+-devel',
            'lilypondcairo',
            'poppler-devel',
            ]
    configure_flags = (target.AutoBuild.configure_flags
                       + ' --without-cups'
                       )

class Epdfview__mingw (Epdfview):
    patches = ['epdfview-0.1.7-mingw.patch']
