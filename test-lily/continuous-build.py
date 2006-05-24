#!/usr/bin/python
import sys
import os


BUILD_PLATFORM=sys.argv[1]
BRANCH=sys.argv[2]
SMTPSERVER=sys.argv[3]

def system (c):
    print c
    if os.system (c):
	raise 'barf'
    

cmd = "make BRANCH=%(BRANCH)s download" % locals () 

plats = ['freebsd', 'mingw', 'darwin-x86', 'linux', 'darwin-ppc']
plats = [p for p in plats if p <> 'darwin-ppc']

cmd +=  ''' && python test-gub.py --smtp %(SMTPSERVER)s
--to hanwen@xs4all.nl 
--from builddaemon@lilypond.org --repository downloads/lilypond-%(BRANCH)s/
--smtp %(SMTPSERVER)s --quiet''' % locals ()


for p in plats:
    if os.path.exists ('target/%s/system/etc/gup/lock' % p):
        continue
    
    cmd += ' "python gub-builder.py --branch %(BRANCH)s -p %(p)s build lilypond"' % locals()

cmd = cmd.replace ('\n',' ') 
system (cmd)

 
