from gub import toolsbuild

class Texi2html__tools (toolsbuild.AutoBuild):
    source = 'http://lilypond.org/vc/texi2html.git&branch=master'
    def get_build_dependencies (self):
        return ['git']
