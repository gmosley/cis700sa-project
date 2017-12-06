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

echo "running flawfinder"
flawfinder --quiet --column --dataonly --singleline $SOURCE_FILE > results/flawfinder.txt
if [ ! $? -eq 0 ]; then
    echo "error running flawfinder"
fi

mkdir results/cppcheck
echo "running cppcheck"
cppcheck --plist-output=results/cppcheck $SOURCE_FILE 2> results/cppcheck.txt > results/cppcheck_log.txt
if [ ! $? -eq 0 ]; then
    echo "error running cppcheck"
fi

echo "running infer"
infer run -o results/infer -a checkers --bufferoverrun -- $BUILD_COMMAND 2> results/infer.txt > results/infer_log.txt
if [ ! $? -eq 0 ]; then
    echo "error running infer"
fi

echo "running scan-build"
scan-build -o results/scan-build -plist-html $BUILD_COMMAND 2> results/scan-build.txt > results/scan-build_log.txt
if [ ! $? -eq 0 ]; then
    echo "error running scan-build"
fi
