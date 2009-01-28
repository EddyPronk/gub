# Ugh.

# We cannot just go for python3 syntax and amend python2's urllib by
# doing
#    import urllib2 as request
# see note in gub/__init__.py

from urllib.request import *
