#!/bin/sh
set -x

mkdir -p $HOME/test-gub/ \
 && cd $HOME/test-gub \
 && rm -rf bin/ lilypond \
 && sh $1 --batch --prefix `pwd` \
 && bin/lilypond typography-demo


