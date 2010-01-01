#
from gub import context
from gub import misc
from gub import target
from gub.specs import lilypond

class LilyPond_test (lilypond.LilyPond_base):
    @context.subst_method
    def test_ball (self):
        return '%(uploads)s/lilypond-%(version)s-%(build_number)s.test-output.tar.bz2'
    make_flags = misc.join_lines ('''
CPU_COUNT=%(cpu_count)s
''')
    compile_flags = lilypond.LilyPond_base.compile_flags + ' test'
        #return (lilypond.LilyPond_base.install_command
    install_command = 'true'
    def install (self):
        target.AutoBuild.install (self) 
        self.system ('''
LD_PRELOAD= tar -C %(builddir)s -cjf %(test_ball)s input/regression/out-test
''')

Lilypond_test = LilyPond_test
