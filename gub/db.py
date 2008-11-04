# Get a simple database module  -- gdbm is not generally available

try:
    import gdbm as db
except:
    try:
        import dbm as db
    except:
        try:
	    import dbhash as db
	except Exception, e:
	    print 'No db module found'
	    raise e
