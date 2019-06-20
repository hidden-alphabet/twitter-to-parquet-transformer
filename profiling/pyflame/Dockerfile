# usage: docker run \
#           --rm \
#           --privileged \
#           -v $PWD:$PWD \
#           --cap-add SYS_PTRACE \
#           pyflame \
#             -o $PWD/profile.txt \
#             -t python -c 'for x in range(1000): print(x)'
FROM ubuntu:bionic
LABEL maintainer "Cole Hudson <cole@colejhudson.com>"

RUN apt-get update -y && \
    apt-get install -y \
      git \
      g++ \
      make \
      libtool \
      autoconf \
      automake \
      pkg-config \
      autotools-dev \
      python-dev \
      python3-dev

RUN git clone https://github.com/uber/pyflame.git

RUN cd pyflame && ./autogen.sh && ./configure && make

RUN cp ./pyflame/src/pyflame /usr/local/bin/pyflame

ENTRYPOINT ["pyflame"]
