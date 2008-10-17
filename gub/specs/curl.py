from gub import targetbuild

class Curl (targetbuild.TargetBuild):
    source = 'http://curl.haxx.se/download/curl-7.19.0.tar.gz'
    def install (self):
        targetbuild.TargetBuild.install (self)
        self.system ('mkdir -p %(install_prefix)s%(cross_dir)s/bin')
        self.system ('mv %(install_prefix)s/bin/curl-config %(install_prefix)s%(cross_dir)s/bin/curl-config')
        self.system ('sed -e "s@%(system_prefix)s@%(prefix_dir)s@g" > %(install_prefix)s/bin/curl-config < %(install_prefix)s%(cross_dir)s/bin/curl-config')
