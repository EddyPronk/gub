from gub import target

class Pixman (target.AutoBuild):
    source = 'http://www.cairographics.org/releases/pixman-0.13.2.tar.gz'
    dependencies = ['libtool']

class Pixman__linux__ppc (Pixman):
    patches = ['pixman-0.13.2-auxvec.patch']
