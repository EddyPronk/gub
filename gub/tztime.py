import time
import re

default_format = '%Y-%m-%d %H:%M:%S %z'

def parse (str, fmt=default_format):
    f = fmt.replace (' %z', '')
    m = re.search  ('(.*) ([+-][0-9]*)', str)
    date = str
    tz = None
    if m:
        date = m.group (1)
        tz = m.group (2)
    return tuple (list (time.strptime (date, f)) + [tz])

def format (tup, fmt=default_format):
    f = fmt.replace ('%z', '%%(z)s')
    z = tup[9]
    if not z:
        z = '+0000'
    return time.strftime (f, tup[:9]) % locals ()

def test ():
    date = '2007-09-14 11:39:21 +0200'
    printf (parse (date))
    printf (format (parse (date)))

    date = '2007-09-14 11:39:21'
    printf (parse (date))
    printf (format (parse (date)))
    
if __name__ == '__main__':
    test ()
    
    
