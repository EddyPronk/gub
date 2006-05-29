#!/bin/sh


BUILD_PLATFORM="$1"
BRANCH="$2"
SMTPSERVER="$3"

set -x

echo Build at `date`

PYTHONPATH=target/$BUILD_PLATFORM/src/lilypond-$BRANCH/python:$PYTHONPATH

make BRANCH=$BRANCH download \
&& python test-gub.py --to hanwen@xs4all.nl --to lilypond-cvs@gnu.org \
   --from builddaemon@lilypond.org --repository downloads/lilypond-$BRANCH/  \
    --smtp $SMTPSERVER --quiet "make BRANCH=$BRANCH $BUILD_PLATFORM" \
&& python test-gub.py --to hanwen@xs4all.nl --to lilypond-cvs@gnu.org \
   --from builddaemon@lilypond.org --repository downloads/lilypond-$BRANCH/  \
    --smtp $SMTPSERVER --quiet "make BRANCH=$BRANCH doc-build" \
&& python test-lily/rsync-lily-doc.py \
    --recreate \
    --output-distance target/$BUILD_PLATFORM/src/lilypond-$BRANCH/scripts/output-distance.py \
    target/$BUILD_PLATFORM/build/lilypond-$BRANCH/out-www/web-root \
## clean
&& find target/$BUILD_PLATFORM/build/lilypond-$BRANCH/ -name 'lily-[0-9]*' -mtime +1   -exec rm '{}' ';' \
&& rm -f target/$BUILD_PLATFORM/build/lilypond-$BRANCH/Documentation/user/out-www/{lilypond,lilypond-internals,music-glossary}.* 

 
