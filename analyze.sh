#!/usr/bin/env bash

SOURCE_FILE=itc_benchmarks/01.w_Defects/null_pointer.c
BUILD_COMMAND="clang -c -I itc_benchmarks/include/ $SOURCE_FILE"

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
