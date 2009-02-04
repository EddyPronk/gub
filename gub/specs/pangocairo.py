from gub.specs import pango

class Pangocairo (pango.Pango):
#    source = 'http://ftp.gnome.org/pub/GNOME/platform/2.22/2.22.0/sources/pango-1.20.0.tar.bz2'
    source = 'http://ftp.acc.umu.se/pub/GNOME/platform/2.25/2.25.5/sources/pango-1.22.4.tar.gz'
    patches = pango.Pango.patches #['pango-1.20-substitute-env.patch']
    def get_build_dependencies (self):
        return pango.Pango.get_build_dependencies (self) + ['cairo-devel']
    def get_conflict_dict (self):
        return {'': ['pango', 'pango-devel', 'pango-doc'], 'devel': ['pango', 'pango-devel', 'pango-doc'], 'doc': ['pango', 'pango-devel', 'pango-doc'], 'runtime': ['pango', 'pango-devel', 'pango-doc']}
    def XXXconfigure_command (self):
        return (pango.Pango.configure_command (self)
                + ''' LDFLAGS='%(rpath)s' ''')
    def configure (self):
        pango.Pango.configure (self)
        #FIXME: add to update_libtool ()
        def libtool_disable_rpath (logger, libtool, file):
            from gub import loggedos
            loggedos.file_sub (logger, [('^(hardcode_libdir_flag_spec)=.*',
                                         (r'hardcode_libdir_flag_spec="-Wl,-rpath -Wl,\$libdir'
                                          + self.expand (' %(rpath)s"').replace ('\\$$', "'$'")))],
                               file)
        self.map_locate (lambda logger, file: libtool_disable_rpath (logger, self.expand ('%(system_prefix)s/bin/libtool'), file), '%(builddir)s', 'libtool')
