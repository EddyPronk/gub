# Get a simple database module  -- gdbm is not generally available

try:
    import gdbm as db
except:
    try:
        import dbm as db
    except:
        try:
            import dbhash as db
        except:
            print 'No db module found'
            raise
