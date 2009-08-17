from gub import target

class Epdfview (target.AutoBuild):
    source = 'http://trac.emma-soft.com/epdfview/chrome/site/releases/epdfview-0.1.7.tar.gz'
    def _get_build_dependencies (self):
        return [
            'tools::automake',
            'tools::gettext',
            'tools::libtool',
            'tools::pkg-config',
            'gtk+-devel',
            'lilypondcairo',
            'poppler-devel',
            ]
