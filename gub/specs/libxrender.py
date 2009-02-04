from gub import target

class Libxrender (target.AutoBuild):
    source = 'http://xorg.freedesktop.org/releases/X11R7.4/src/everything/libXrender-0.9.4.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'libx11-devel', 'libxdmcp-devel', 'renderproto-devel']
    def XXXconfigure_command (self):
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
