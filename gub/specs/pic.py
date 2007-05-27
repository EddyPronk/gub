import glob
import os
import re
import shutil
import cvs
from gub import gubb
from gub import misc
from gub import targetpackage

pic_cvs = ':pserver:anonymous@gforge.natlab.research.philips.com:/cvsroot/pfgpsc'

class Pic (targetpackage.TargetBuildSpec):
    def get_dependency_dict (self):
        return {'': []}

    def get_subpackage_names (self):
        return ['']
    
    def force_sequential_build (self):
        ## upnpAllegro is broken
        return True

    def get_build_dependencies (self):
        neon_debian = ['comerr-dev',
                       'libcomerr2',
                       'libneon24-dev',
                       'libssl0.9.8',
                       'libkrb53',
                       'libxml2',
                       'zlib1g',
                       ]
        return [
                'libbluetooth1-dev',
                'libboost-dev',
                'libboost-filesystem-dev',
                'libboost-thread1.32.0',
                'libboost-thread-dev',
                'libdbi0-dev',
                'libexif-dev',
                'libgphoto2-2-dev',
                'libid3-3.8.3-dev',
                'libobexftp-dev',
                'libopenobex-1.0-0-dev',
                'libstdc++5',
                'libstdc++5-3.3-dev',
                'libusb-dev',
                'libxerces26',
                'libxerces26-dev',
                'uuid-dev',
                'zlib1g-dev',
                ]

    def get_unstable_build_dependencies (self):
        neon_debian = ['comerr-dev',
                       'libcomerr2',
                       'libneon25-dev',
                       'libssl0.9.8',
                       'libkrb53',
                       'libxml2',
                       'zlib1g',
                       ]
        return [
                'libbluetooth1-dev',
                'libboost-dev',
                'libboost-filesystem-dev',
                'libboost-thread-dev',
                'libdbi0-dev',
                'libexif-dev',
                'libgphoto2-2-dev',
                'libid3-3.8.3-dev',
                'libobexftp-dev',
                'libopenobex-1.0-0-dev',
                'libusb-dev',
                'libxerces26c2',
                'libxerces26-dev',
                'uuid-dev',
                ]

    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        # FIXME: lilypond_branch
        self.with_template (version=settings.lilypond_branch, mirror=pic_cvs,
                   vc_type='cvs')

        # FIXME: should add to C_INCLUDE_PATH
        builddir = self.builddir ()
        self.target_gcc_flags = (settings.target_gcc_flags
                    + ' -I%(builddir)s' % locals ())
        self._downloader = self.cvs

    def rsync_command (self):
        c = targetpackage.TargetBuildSpec.rsync_command (self)
        c = c.replace ('rsync', 'rsync --delete') # --exclude configure')
        return c

    def configure_command (self):
        return (targetpackage.TargetBuildSpec.configure_command (self)
                + misc.join_lines ('''
--enable-media-server
--disable-decui
--enable-static-gxx
'''))

    def patch (self):
        self.system ('''
sed -i 's/neon//' %(srcdir)s/comps/decDemo/CMakeLists.txt
sed -i 's/id3/id3 z/' %(srcdir)s/comps/mtmTools/CMakeLists.txt
sed -i 's/gphoto2_port/gphoto2_port dl/' %(srcdir)s/comps/mtmUsb/CMakeLists.txt
''')

    def configure (self):
        targetpackage.TargetBuildSpec.configure (self)
        self.system ('''
echo '#define HAVE_OBEXFTP_CLIENT_BODY_CONTENT 1' >> %(builddir)s/build/config.h
''')
#'

    def compile_command (self):
        return (targetpackage.TargetBuildSpec.compile_command (self)
            + ' mediaServer')

    def install_command (self):
        return 'mkdir -p %(install_prefix)s/bin && cp -pv %(builddir)s/build/bin/mediaServer %(install_prefix)s/bin'

    # FIXME: shared for all CVS packages
    def srcdir (self):
        return '%(allsrcdir)s/%(name)s-%(version)s'

    # FIXME: shared for all CVS packages
    def builddir (self):
        return '%(targetdir)s/build/%(name)s-%(version)s'

    def name_version (self):
        # whugh
        if os.path.exists (self.srcdir ()):
            d = misc.grok_sh_variables (self.expand ('%(srcdir)s/VERSION'))
            return 'pic-%(VERSION)s' % d
        #return targetpackage.TargetBuildSpec.name_version (self)
        return 'pic-1.67'

    def install (self):
        targetpackage.TargetBuildSpec.install (self)

    def gub_name (self):
        nv = self.name_version ()
        p = self.settings.platform
        return '%(nv)s.%(p)s.gub' % locals ()

#Hmm
Pic__mipsel = Pic
