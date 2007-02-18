"""
    Copyright (c) 2005--2007
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
"""

import os
import fcntl

class LockedError (Exception):
    pass
    
class Locker:
    def __init__ (self, lock_file_name):
        self.lock_file = None
        self.lock_file_name = None
        
        lock_file = open (lock_file_name, 'a')
        lock_file.write ('')

        try:
            fcntl.flock (lock_file.fileno (),
                         fcntl.LOCK_EX | fcntl.LOCK_NB)
        except IOError:
            raise LockedError ("Can't acquire lock: " + lock_file_name)

        self.lock_file_name = lock_file_name
        self.lock_file = lock_file

    def unlock (self):
        if self.lock_file_name:
            os.remove (self.lock_file_name)
            
        if self.lock_file:
            fcntl.flock (self.lock_file.fileno(), fcntl.LOCK_UN)
	
    def __del__ (self):
	self.unlock ()
