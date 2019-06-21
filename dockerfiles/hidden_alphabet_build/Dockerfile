FROM amazonlinux:2017.03

ENV HOME /

RUN yum -y install \
      jq \
      git \
      zip \
      make \
      unzip \
      python36 \
      python36-pip

COPY ./credentials $HOME/.aws/credentials

RUN pip-3.6 install --upgrade pip

RUN pip install --upgrade awscli

RUN pwd

RUN git clone https://github.com/lambda-labs-13-stock-price-2/twitter-to-parquet-transformer.git

RUN cd twitter-to-parquet-transformer && make bundle

RUN rm -rf $HOME/.aws
