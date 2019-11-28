#!/usr/bin/env bash

DB_FOLDER='/home/louis/.cache/ieml/1.0.3/e116865545e9e8132dd87e6d62d01040'


pushd $DB_FOLDER
# start with structure
mkdir structure
rm -f structure/dictionary

for f in dictionary/structure/*; do
    perl -pe 'chomp if eof' $f >> structure/dictionary
    printf "\n\n"  >> structure/dictionary
done

mkdir descriptors

for l in fr en;
do
    mkdir descriptors/$l

    for k in translations comments;
    do
        rm descriptors/$l/$k

        for f in dictionary/descriptors/$l/$k/*; do
            perl -pe 'chomp if eof' $f >> descriptors/$l/$k
            printf "\n"  >> descriptors/$l/$k
        done
    done
done


popd
