import glob
import os
import re
import shutil
import cvs
import gub
import misc
import targetpackage

pic_cvs = ':pserver:anonymous@gforge.natlab.research.philips.com:/cvsroot/pfgpsc'

from context import *

class Pic (targetpackage.TargetBuildSpec):
    def get_dependency_dict (self):
        return {'': []}

    def get_subpackage_names (self):
        return ['']
    
    def broken_for_distcc (self):
        ## upnpAllegro is broken
        return True

    def get_build_dependencies (self):
        return ['libdbi0-dev', 'libboost-dev']

    def __init__ (self, settings):
        targetpackage.TargetBuildSpec.__init__ (self, settings)
        # FIXME: lilypond_branch
        self.with (version=settings.lilypond_branch, mirror=pic_cvs,
                   track_development=True)

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

#    def configure (self):
#        self.autoupdate ()

    def compile_command (self):
        return (targetpackage.TargetBuildSpec.compile_command (self)
            + ' mediaServer')

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
