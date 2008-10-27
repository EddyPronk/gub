from gub import mirrors
from gub import targetbuild

class Regex (targetbuild.AutoBuild):
    source = mirrors.with_template (name='regex', version='2.3.90-1',
                   mirror=mirrors.lilypondorg, format='bz2')
