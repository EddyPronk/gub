from gub import target

class Librsvg (target.AutoBuild):
    source = 'http://ftp.gnome.org/pub/GNOME/sources/librsvg/2.22/librsvg-2.22.3.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'cairo-devel', 'fontconfig-devel', 'libglib-devel', 'libgtk+-devel', 'pangocairo-devel', 'libxml2-devel']
    def configure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ''' LDFLAGS='%(rpath)s' ''')
