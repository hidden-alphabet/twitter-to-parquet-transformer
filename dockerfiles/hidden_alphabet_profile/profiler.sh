#!/usr/bin/env bash

HTML=tweets.html
STACKTRACE=profile.txt
FLAMEGRAPH=flamegraph.svg

USERAGENT="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0"

curl \
  -H "User-Agent: ${USERAGENT}" \
  "https://twitter.com/search?q=tesla%20lang%3Aen%20since%3A2014-01-01%20&src=typd" \
  > $HTML

pyflame -s 10 -o $STACKTRACE -t python3 script.py $HTML

echo 'Creating flamegraph.'

flamegraph $STACKTRACE > $FLAMEGRAPH
