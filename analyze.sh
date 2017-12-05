#!/usr/bin/env bash

SOURCE_FILE=$1
BUILD_COMMAND="clang -c $SOURCE_FILE"

if [[ $# -eq 0 ]] ; then
    echo "usage ./analyze <source.c>"
    exit 1
fi

if [ ! -f $SOURCE_FILE ]; then
    echo "$SOURCE_FILE not found!"
    exit 1
fi

rm -rf results
mkdir results

# only output option is text
flawfinder --quiet --column --dataonly --singleline $SOURCE_FILE > results/flawfinder.txt

# also has the option to output xml
mkdir results/cppcheck
cppcheck --plist-output=results/cppcheck $SOURCE_FILE 2> results/cppcheck.txt

# need to look more at options for infer
# using debug flag will report more bugs
infer run -o results/infer -a checkers --bufferoverrun -- $BUILD_COMMAND 2> results/infer.txt

scan-build -o results/scan-build -plist-html $BUILD_COMMAND 2> results/scan-build.txt
