#!/usr/bin/env bash

FILE=$PWD/profiling/example.html
CMD=$PWD/profiling/test.py

docker run \
    -v $PWD:$PWD \
    --cap-add SYS_PTRACE \
    html_to_parquet \
    --flamegraph \
    -o $PWD/profile.txt \
    -t python3 $CMD $FILE

docker run flamegraph $PWD/profile.txt > flamegraph.svg

open -a "Google Chrome" flamegraph.svg
