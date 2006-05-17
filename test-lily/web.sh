#!/bin/sh


BUILD_PLATFORM="$1"
BRANCH="$2"
SMTPSERVER="$3"

set -x

echo Build at `date`

make BRANCH=$BRANCH download \
&& python test-gub.py --to hanwen@xs4all.nl --to janneke@gnu.org \
   --from builddaemon@lilypond.org --repository downloads/lilypond-$BRANCH/  \
    --smtp $SMTPSERVER --quiet "make BRANCH=$BRANCH $BUILD_PLATFORM" \
&& python test-gub.py --to hanwen@xs4all.nl --to janneke@gnu.org \
   --from builddaemon@lilypond.org --repository downloads/lilypond-$BRANCH/  \
    --posthook "find target/$BUILD_PLATFORM/build/lilypond-$BRANCH/ -name 'lily-[0-9]*' -mtime +1   -exec rm '{}' ';' -print" \
    --smtp $SMTPSERVER --quiet "make BRANCH=$BRANCH doc" \


 
