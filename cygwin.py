#!/usr/bin/python
# debug helper for python-mode's jumping to exception file:line errors

#import "gub-builder" as gub_builder
import gub_builder
import sys

sys.argv = ['bar', '--target-platform=cygwin', '--keep', 'build', 'lilypond']
gub_builder.main ()
