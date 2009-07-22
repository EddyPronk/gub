import hashlib

def md5 (string=''):
    return hashlib.md5 (string.encode ('utf8'))

new = md5
blocksize = 1        # legacy value (wrong in any useful sense)
digest_size = 16
