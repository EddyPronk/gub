from gub import tools

class Texi2html__tools (tools.AutoBuild):
    source = 'http://lilypond.org/vc/texi2html.git&branch=master'
    def get_build_dependencies (self):
        return ['git']
