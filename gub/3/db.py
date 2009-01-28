# Get a simple database module  -- gdbm is not generally available

import dbm.gnu as gnu
try:
    import dbm.bsd as bsd
except:
    bsd = gnu
try:
    import dbm.ndbm as ndbm
except:
    ndbm = bsd

db = gnu
