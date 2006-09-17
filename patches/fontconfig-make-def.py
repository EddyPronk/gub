#!/usr/bin/env python

import re
import os
import sys


funcs = ['FcConfigGetCacheDirs',
         'FcDirCacheRead',
         'FcCacheDir',
         'FcCacheNumFont',
         'FcCacheNumSubdir',
         'FcCacheSubdir',
         'FcConfigEnableHome',
         'FcConfigGetCacheDirs',
         'FcDirCacheLoad',
         'FcDirCacheLoadFile',
         'FcDirCacheRead',
         'FcDirCacheUnlink',
         'FcDirCacheUnload',
         'FcStrFree',
         'FcStrPlus',
         'FcFileIsDir',
         'FcCacheCopySet',
         'FcPatternGetString',

         ## pango:
         'FcFontSetSortDestroy',
         'FcPatternDuplicate',
         'FcPatternGetBool',
         'FcPatternGetCharSet',
         'FcPatternGetDouble',
         'FcPatternGetMatrix',
         'FcPatternReference',
         'FcPatternAddBool',
         'FcPatternAddDouble',
         'FcPatternAddMatrix',
         'FcPatternAddString',
         'FcPatternAddCharSet',
         'FcPatternAddLangSet',
         
         ]

forbidden = ['FcMatrixInit', 'FcConfigNormalizeFontDir']


def note_func (match):
    name = match.group (1)
    if name not in forbidden:
        funcs.append (name)

for a in sys.argv[1:]:
    re.sub ('@FUNC@\s+(.*)\n',  note_func, open (a).read ())


sys.stdout.write ('''EXPORTS
%s
LIBRARY libfontconfig-@LT_CURRENT_MINUS_AGE@.dll
VERSION @LT_CURRENT@.@LT_REVISION@
'''
                  % ('\n'.join ('\t' + f for f in funcs)))
