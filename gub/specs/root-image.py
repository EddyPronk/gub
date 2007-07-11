from gub import gubb

class Root_image (gubb.NullBuildSpec):
    def __init__ (self, settings):
        gubb.NullBuildSpec.__init__ (self, settings)
        from gub import repository
        self.with_vc (repository.Version ('1.0'))
    def get_build_dependencies (self):
        return [
            'base-files',
            'base-passwd',
            'busybox',
            'dhcp',
            'dropbear',
            'psmisc',
            'sysvinit',
            ]
    def get_dependency_dict (self):
        return {'': self.get_build_dependencies ()}
    def get_ipkg_dependencies (self):
        return [
            'initscripts',
            'linux-hotplug',
            'makedevs',
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
#            'tinylogin',
#Reading pipe: tar -tzf "/home/janneke/vc/gub-samco/uploads/linux-arm-vfp/sysvinit-2.86.linux-arm-vfp.gup"
#already have file ./sbin/sulogin: tinylogin
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
cd %(install_root)s && ar p %(f)s data.tar.gz | tar -zx%(v)sf -
''', locals ())
    def install (self):
        gubb.NullBuildSpec.install (self)
        for i in self.get_ipkg_dependencies ():
            self.install_ipkg (i)
