from gub import target

class Librsvg (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/librsvg/2.26/librsvg-2.26.0.tar.gz'
    dependencies = ['tools::libtool',
                'cairo-devel',
                'fontconfig-devel',
                'glib-devel',
                'gtk+-devel',
                'pangocairo-devel',
                'libxml2-devel']

class Librsvg__darwin (Librsvg):
    dependencies = [x for x in Librsvg.dependencies
                if x.replace ('-devel', '') not in [
                'libxml2', # Included in darwin-sdk, hmm?
                ]]
