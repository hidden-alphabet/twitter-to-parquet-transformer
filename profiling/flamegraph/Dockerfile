# usage: docker run \
#           -v $PWD:$PWD \
#           -w $PWD \
#           flamegraph profile.txt \
#           > flamegraph.svg
FROM ubuntu:bionic
LABEL maintainer "Cole Hudson <cole@colejhudson.com>"

ENV LC_ALL=C.UTF-8

RUN apt-get update -y && \
    apt-get install -y git

RUN git clone https://github.com/brendangregg/FlameGraph.git

RUN chmod +x ./FlameGraph/flamegraph.pl && \
    ln -s $(pwd)/FlameGraph/flamegraph.pl /usr/bin/flamegraph

ENTRYPOINT ["flamegraph"]

CMD ["-h"]
