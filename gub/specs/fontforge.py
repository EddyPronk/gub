from gub import toolsbuild 

class Fontforge (toolsbuild.ToolsBuild):
    source = ('http://lilypond.org/gub-sources/fontforge_full-20060501.tar.bz2'
              + '&patch=fontforge-20060501-srcdir.patch'
              + '&patch=fontforge-20060501-execprefix.patch')
    auto_source = mirrors.with_template (name='fontforge', mirror='http://lilypond.org/download/gub-sources/fontforge_full-%(version)s.tar.bz2',
                   version="20060501")
    def get_build_dependencies (self):
        return ['freetype']
    def patched_through_source_url_now (self):
        self.apply_patch ('fontforge-20060501-srcdir.patch')
        self.apply_patch ('fontforge-20060501-execprefix.patch')
    def configure_command (self):
        return (toolsbuild.ToolsBuild.configure_command (self)
                + ' --without-freetype-src')
    def srcdir (self):
        return toolsbuild.ToolsBuild.srcdir (self).replace ('_full', '')
    def install_command (self):
        return self.broken_install_command ()
    def packaging_suffix_dir (self):
        return ''
