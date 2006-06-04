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
            raise LockedError ("Can't acquire", lock_file)

        self.lock_file_name = lock_file_name
        self.lock_file = lock_file

    def unlock (self):
        if self.lock_file_name:
            os.remove (self.lock_file_name)
            
        if self.lock_file:
            fcntl.flock (self.lock_file.fileno(), fcntl.LOCK_UN)
	
    def __del__ (self):
	self.unlock ()
