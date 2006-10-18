#!/usr/bin/python
import sys
import os
import re
import time


def system (c, ignore_error=False):
    print 'executing' , c
    s = os.system (c)
    if s and not ignore_error:
        raise 'barf'




##
## format:
## 
## "platform": ("login", "host", "directory", test-file")
##
test_settings = eval (open ('test-settings.py').read ())
    

platform_test_aliases = {
    'linux-x86': 'shar',
    'linux-64': 'unix',
    'freebsd-x86': 'unix'
}

def test_build (bin):
    if bin.find (':') < 0:
        bin = os.path.abspath (bin)

    base = os.path.split (bin)[1]

    platform = ''
    for p in ('linux-x86', 'freebsd', 'darwin-ppc', 'darwin-x86', 'mingw'):
        if re.search (p, base):
            platform = p
            break

    if not platform:
        print 'unknown platform for', bin
        return

    ending_found = 0 
    for e in ['.sh', '.zip', '.exe', 'tar.bz2']:
        ending_found = ending_found or base.endswith  (e)

    if not ending_found:
        print 'unknown extension for', base
        return
    
    
    
    try:
        os.unlink ('typography-demo.pdf')
    except:
        pass

    print 'testing platform %s' % platform
    logdir = "log/"
    try:
        (uid, host, dir, test_file) = test_settings[platform]
        if test_file == None:
            test_file = 'test-lily/typography-demo.ly' 
            
        base_test_file = os.path.split (test_file)[1]
        base_test_file_stem = os.path.splitext (base_test_file)[0]

        system ('ssh %(uid)s@%(host)s mkdir  %(dir)s' % locals (), ignore_error=True)
        system ('ssh %(uid)s@%(host)s rm  %(dir)s/%(base_test_file_stem)s.*' % locals (), ignore_error=True)
        

        test_platform = platform_test_aliases.get (platform, platform)
        system ('scp %(test_file)s test-lily/test-%(test_platform)s-gub.sh '
                ' %(bin)s '
                ' %(uid)s@%(host)s:%(dir)s/'
                % locals())


        system ('ssh %(uid)s@%(host)s sh %(dir)s/test-%(test_platform)s-gub.sh %(dir)s %(base)s %(base_test_file)s'
                % locals())
        system ('scp %(uid)s@%(host)s:%(dir)s/%(base_test_file_stem)s.pdf %(logdir)s/%(base)s.test.pdf'
                % locals ())
        system ('xpdf %(logdir)s/%(base)s.test.pdf'
                % locals ())
        
    except KeyError:
        system ('touch %(logdir)s/%(base)s.test.pdf' % locals ())
    

pids = []
for a in sys.argv[1:]:
    pid = os.fork () 
    if not pid:
        test_build (a)
        sys.exit (0)
    else:
        pids.append (pid)

os.wait()
