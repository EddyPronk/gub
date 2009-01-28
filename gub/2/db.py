# Get a simple database module  -- gdbm is not generally available

import dbhash as bsd
try:
    import dbm as ndbm
except:
    ndbm = bsd
try:
    import gdbm as gnu
except:
    gnu = ndbm

db = gnu
