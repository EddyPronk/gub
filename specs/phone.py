import repository
import targetpackage

class Phone (targetpackage.TargetBuildSpec):
    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        repo = repository.Subversion (
            dir=self.get_repodir (),
            source='svn+ssh://gforge.natlab.research.philips.com/svnroot/public/samco',
            branch='branches',
            module='nxpp',
            revision='773')

        self.with_vc (repo)

    def configure_command (self):
        return (targetpackage.TargetBuildSpec.configure_command (self)
                + ' LDFLAGS="-L%(system_root)s/usr/lib -L%(system_root)s/usr/lib/dbd" --disable-audio --disable-sdl')

    def patch (self):
        self.system ('cd %(srcdir)s && echo "Philips Research Unreleased" > LICENSE')
        self.file_sub ([('s3', 'disable_s3')], '%(srcdir)s/configure.ac.in')
        self.system ('''cd %(srcdir)s && ./autogen.sh''')

    def license_file (self):
        return '%(srcdir)s/LICENSE'

    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)

    def get_build_dependencies (self):
        return [#'libavcodec-dev'
            'expat',
            'libavformat-dev', #TBD
            'libboost-dev',
            'libboost-date-time-dev',
            'libboost-filesystem-dev',
            'libboost-iostreams-dev',
            'libboost-thread1.33.1',
            'libboost-thread-dev',
            'libcppunit-dev',
            'libdbi-drivers',
            'libdral',
            'libmobtv',
            'libncurses5-dev',
            'libqt4-dev',
            'libtool',
            'pkg-config',
            'libsqlite3-0',
            'libxml2-dev',
            'sqlite3',
            'libsqlite3-dev',
            'pjproject',
            'libxerces27',
            'libxerces27-dev',
            'uuid-dev',
            'zlib1g-dev',
            ]

    def get_dependency_dict (self):
#        return {'': ['libavcodec']}
        return {'': ['libavformat']}

    def compile_command (self):
        return (targetpackage.TargetBuildSpec.compile_command (self)
                + ' phone')

    def install_command (self):
        return (targetpackage.TargetBuildSpec.install_command (self)
                + ' -C app/phone')

Phone__arm = Phone
