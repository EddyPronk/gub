from gub import target

class Cairo (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/cairo-1.8.6.tar.gz'
    def get_build_dependencies (self):
        return ['tools::libtool', 'fontconfig-devel', 'libpng-devel', 'libx11-devel', 'libxrender-devel', 'pixman-devel']
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

class Cairo__mingw (Cairo):
    source = Cairo.source
    def get_build_dependencies (self):
        return [x for x in Cairo.get_build_dependencies (self)
                if 'libx' not in x]
