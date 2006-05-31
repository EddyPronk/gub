#!/usr/bin/env python
import optparse
import sys
import os
import fcntl

def parse_options ():
    p = optparse.OptionParser ()
    p.usage = "with-lock.py FILE COMMAND"
    p.add_option ('--skip',
		  action="store_true",
		  dest="skip",
		  help="return 0 if couldn't get lock.")
    
    (o,a) = p.parse_args ()
    if len (a) < 2:
	p.print_help()
	sys.exit (2)
	
    return o,a

def main ():
    (opts, args) = parse_options ()

    lock_file_name = args[0]
    cmd = args[1]

    ## need to include binary too.
    args = args[1:]
    
    lock_file = open (lock_file_name, 'w')
    lock_file.write ('')

    try:
	fcntl.flock (lock_file.fileno (),
		     fcntl.LOCK_EX | fcntl.LOCK_NB)

    except IOError:
	print "Can't acquire lock %s" % lock_file_name
	if opts.skip:
	    sys.exit (0)
	else:
	    sys.exit (1)

    stat = os.spawnvp (os.P_WAIT, cmd, args)
    os.remove (lock_file_name)
    fcntl.flock (lock_file.fileno(), fcntl.LOCK_UN)
    
    sys.exit (stat)
     
if __name__ == '__main__':
    main ()
