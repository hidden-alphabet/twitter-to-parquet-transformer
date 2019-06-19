#!/usr/bin/env bash

FILE=$PWD/example_3.html
CMD=$PWD/test_lambda.py

docker run \
    -v $PWD:$PWD \
    --cap-add SYS_PTRACE \
    html_to_parquet \
    -o $PWD/profile.txt \
    --flamegraph \
    -t python3 $CMD $FILE

cat profile.txt | ./flamegraph.pl > flamegraph.svg

open -a "Google Chrome" flamegraph.svg