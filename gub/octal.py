# During python2 -> python3 transition, keep core code clear of octal
# diff.  Diffs trigger checksum problems.
if 1: #sys.verions.startswith ('2'):
    o644 = 0644
    o755 = 0755
# does not parse
#else:
#    o644 = 0o644
#    o755 = 0o755
