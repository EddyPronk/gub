import hashlib

def md5 (string=''):
    return hashlib.md5 (string.encode ('utf8'))
