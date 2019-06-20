# usage: docker run \
#         --cap-add SYS_PTRACE \
#         hidden_alphabet:twitter-transformer-profiling \
#         > stacktrace.svg
FROM pyflame:latest
FROM flamegraph:latest

LABEL maintainer "Cole Hudson <cole@colejhudson.com>"

RUN apt-get update -y &&\
    apt-get install -y \ 
      python3-pip \ 
      curl \
      python3-lxml

RUN git clone https://github.com/lambda-labs-13-stock-price-2/twitter-to-parquet-transformer.git && \
    cd twitter-to-parquet-transformer && \
    pip3 install .

RUN mkdir -p /app

COPY --from=0 /usr/local/bin/pyflame /usr/local/bin/pyflame
COPY profiler.sh /app
COPY script.py /app

WORKDIR /app

ENTRYPOINT ["./profiler.sh"]
