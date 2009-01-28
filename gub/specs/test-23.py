import sys
#
from gub import tools

from gub import octal
assert (octal.o644 == 420)
assert (octal.o755 == 493)

from gub.syntax import printf

sys.stdout.write ('\nEXPECT:2 3')
sys.stdout.write ('\n>>>')
printf (2,3)
sys.stdout.write ('<<<\n')

sys.stdout.write ('\nEXPECT: (2, 3)')
sys.stdout.write ('\n>>>')
printf ((2,3))
sys.stdout.write ('<<<\n')

import md5
printf ( md5.md5 ('foo'))

import new
new.classobj ('foo', (tools.NullBuild,), {})

class Test_23 (tools.NullBuild):
    source = 'url://host/test-23-1.0.tar.gz'
    def untar (self):
        pass
    def install (self):
        self.system ('mkdir -p %(install_root)s%(system_prefix)s')

sys.stdout.write ('''\nEXPECT: <class 'test-23.Test_23'>''')
sys.stdout.write ('\n>>>')
printf (Test_23)
sys.stdout.write ('<<<\n')

from gub import settings
from gub import repository
sys.stdout.write ('\nEXPECT:<test-23.Test_23 object at 0x00000>''')
sys.stdout.write ('\n>>>')
printf (Test_23 (settings.Settings (), repository.Version ('test-23')))
sys.stdout.write ('<<<\n')

