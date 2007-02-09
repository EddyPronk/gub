#!/usr/bin/env python
import optparse
import sys
import os


sys.path.insert (0, os.path.split (sys.argv[0])[0] + '/../lib/')

import locker

def parse_options ():
    p = optparse.OptionParser ()
    p.usage = "with-lock.py FILE COMMAND"
    p.add_option ('--skip',
		  action="store_true",
		  dest="skip",
		  help="return 0 if couldn't get lock.")

    p.disable_interspersed_args()


    (o,a) = p.parse_args ()
    if len (a) < 2:
	p.print_help()
	sys.exit (2)
	
    return o,a

def run_command_with_lock (lock_file_name, cmd, args):
    lock_obj = locker.Locker (lock_file_name)
    stat = os.spawnvp (os.P_WAIT, cmd, args)
    return stat

def main ():
    (opts, args) = parse_options ()

    lock_file_name = args[0]
    cmd = args[1]

    ## need to include binary too.
    args = args[1:]


    try:
        stat = run_command_with_lock (lock_file_name, cmd, args)
        sys.exit (stat)
    except locker.LockedError:
	print "Can't acquire lock %s" % lock_file_name
	if opts.skip:
	    sys.exit (0)
	else:
	    sys.exit (1)

if __name__ == '__main__':
    main ()
