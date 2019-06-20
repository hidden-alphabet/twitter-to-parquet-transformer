#!/usr/bin/env bash

# DIR variable from https://stackoverflow.com/a/246128/8738498
DIR="$(cd "$( dirname "${BASH_SOURCE[0]}" )" >/dev/null 2>&1 && pwd)"

CMD=$DIR/test.py
FILE=$DIR/example.html

STACKTRACE=$DIR/profile.txt
FLAMEGRAPH=$DIR/flamegraph.svg.html

USERAGENT="Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:54.0) Gecko/20100101 Firefox/54.0"

curl \
  -H "User-Agent: ${USERAGENT}" \
  "https://twitter.com/search?q=tesla%20lang%3Aen%20since%3A2014-01-01%20&src=typd" \
  > $FILE

docker run \
    --rm \
    -v $PWD:$PWD \
    -w $PWD \
    --cap-add SYS_PTRACE \
    pyflame \
      -o $STACKTRACE \
      -t python3 $CMD $FILE

docker run \
  --rm \
  -v $PWD:$PWD \
  -w $PWD \
  flamegraph $STACKTRACE \
  > $FLAMEGRAPH

swift <<-SWIFT
import AppKit

if let url = URL(string: "file://$FLAMEGRAPH") {
  NSWorkspace.shared.open(url)
}
SWIFT
