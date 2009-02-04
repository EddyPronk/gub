from gub import target

class Libxfixes (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXfixes-4.0.3.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'fixesproto-devel', 'libx11-devel', 'libxau-devel', 'libxdmcp-devel']
    def XXconfigure_command (self):
        return (target.AutoBuild.configure_command (self)
                + ''' LDFLAGS='%(rpath)s' ''')
    def configure (self):
        target.AutoBuild.configure (self)
        #FIXME: add to update_libtool ()
        def libtool_disable_rpath (logger, libtool, file):
            from gub import loggedos
            # Must also keep -rpath $libdir, because when
            # build_arch==target_arch we may run build-time
            # executables.  Either that, or set LD_LIBRARY_PATH
            # somewhere.
            loggedos.file_sub (logger, [('^(hardcode_libdir_flag_spec)=.*',
                                         (r'hardcode_libdir_flag_spec="-Wl,-rpath -Wl,\$libdir'
                                          + self.expand (' %(rpath)s"').replace ('\\$$', "'$'")))],
                               file)
        self.map_locate (lambda logger, file: libtool_disable_rpath (logger, self.expand ('%(system_prefix)s/bin/libtool'), file), '%(builddir)s', 'libtool')

