FROM python

ARG version

RUN apt update && apt install fzf

COPY dist/bq-meta-${version}.tar.gz bq-meta.tar.gz

RUN pip3 install bq-meta.tar.gz
