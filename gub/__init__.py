'''
    Copyright (c) 2005--2009
    Jan Nieuwenhuizen <janneke@gnu.org>
    Han-Wen Nienhuys <hanwen@xs4all.nl>

    This program is free software; you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation; either version 2, or (at your option)
    any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program; if not, write to the Free Software
    Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
'''

'''gub lib'''

import os
import sys

# python2/3 runtime compatibility lib path initialization
# from gub import octal
__path__.insert (0, os.path.join (__path__[0], str (sys.version_info[0])))
__path__.insert (0, os.path.join (__path__[0], str (sys.version_info[1])))

# URG, FIXME.  Python is broken.

# Having gub/2/4/md5.py does not work.  Apparently there is no way we
# can access stuff from the global md5; inside the 'gub' package, every
# `import md5' is taken from inside the 'gub' package.

# So, the only thing we can do is never to shadow a `global' module;
# only have md5.py if it does not exists in this python version.

# python3: import md5 --> gub/3/md5.py
# python2.4: import hashlib --> gub/2/4/hashlib.py
sys.path.insert (0, __path__[1])
sys.path.insert (0, __path__[0])
