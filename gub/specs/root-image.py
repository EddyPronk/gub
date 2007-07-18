from gub import gubb

class Root_image (gubb.NullBuildSpec):
    def __init__ (self, settings):
        gubb.NullBuildSpec.__init__ (self, settings)
        from gub import repository
        self.with_vc (repository.Version ('1.0'))
    def _get_build_dependencies (self):
        busybox = [
            'dhcp',
            'psmisc',
            'sysvinit',
            'tinylogin',
            ]
        return [
            'base-files',
            'base-passwd',
            'busybox',
            'dropbear',
            ]
    def get_build_dependencies (self):
        return self._get_build_dependencies ()
    def get_dependency_dict (self):
        return {'': self._get_build_dependencies ()}
    def get_ipkg_dependencies (self):
        busybox = ['makedevs']
        return [
            'base-files',
            'base-passwd',
            'dev',
            'etc-rc',
            'etc-usr-share',
            'initscripts',
            'linux-hotplug',
            'module-init-tools-depmod',
            'modutils-depmod',
            'modutils-initscripts',
            'netbase',
            'nxpp-dvbh',
            'nxpp-esgplayer-autostart',
            'nxpp-pointercal',
            'nxpp-runme',
            'portmap',
            'setserial',
            'strace',
            'sysvinit-inittab',
            'sysvinit-pidof',
            'tslib-conf',
            'update-rc.d',
            ]
    def get_subpackage_names (self):
        return ['']
    def install_ipkg (self, i):
        import glob
        for f in glob.glob (self.expand ('%(downloads)s/ipk/%(i)s_*.ipk',
                                         locals ())):
            v = ''
            if self.verbose >= self.os_interface.level['command']:
                v = 'v'
            self.system ('''
cd %(install_root)s && ar p %(f)s data.tar.gz | fakeroot tar -zx%(v)sf -
''', locals ())
    def install (self):
        gubb.NullBuildSpec.install (self)
        for i in self.get_ipkg_dependencies ():
            self.install_ipkg (i)

class Root_image__linux__arm__vfp (Root_image):
    def _get_build_dependencies (self):
        return (Root_image._get_build_dependencies (self)
                + ['csl-toolchain-binary',
                   'phone'])
    def get_dependency_dict (self):
        d = Root_image.get_dependency_dict (self)
        d[''] += ['csl-toolchain-binary-runtime']
        return d
    
