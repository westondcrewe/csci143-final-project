FROM postgis/postgis

RUN apt-get update && apt-get install -y \
    less \
    make \
    vim

WORKDIR /tmp/db

RUN mkdir /data && chown postgres /data

COPY schema.sql /docker-entrypoint-initdb.d/01.sql
