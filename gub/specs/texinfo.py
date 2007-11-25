from gub import mirrors
from gub import toolsbuild

<<<<<<< HEAD:gub/specs/texinfo.py
class Texinfo (toolsbuild.ToolsBuild):
    source = mirrors.with_template (name='texinfo', version="4.11",
                                    mirror=mirrors.gnu, format="bz2")
#    patches = 'texinfo-4.8.patch'
=======
class Texinfo(toolpackage.ToolBuildSpec):
    def __init__ (self, settings):
        toolpackage.ToolBuildSpec.__init__ (self, settings)
        self.with_template (version="4.11",
                   mirror=mirrors.gnu, format="bz2")
    def patch_for_48_when_are_we_going_to_versionize_patches (self):
        toolpackage.ToolBuildSpec.patch (self)
        self.system ('cd %(srcdir)s && patch -p1 <  %(patchdir)s/texinfo-4.8.patch')

    ## TODO: should patch out info reader completely.
>>>>>>> 0f6345cf5a28d9fe8e2c8105535536b73f5a7b2c:gub/specs/texinfo.py
