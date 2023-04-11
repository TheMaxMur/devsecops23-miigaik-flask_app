FROM python:3.11.3-slim-buster

COPY . /app

RUN apt update && \
    apt install libmariadb-dev g++ libpq-dev gcc exiftool sudo -y 

RUN python3 -m pip install -r /app/requirements.txt

RUN groupadd python && \
    useradd python -g python && \
    rm /usr/bin/env

RUN chown -R python:python /app

WORKDIR /app

RUN usermod -s /usr/sbin/nologin python &&\
    rm /bin/bash &&\
    rm /bin/sh

USER python 

CMD ["flask", "run", "--host=0.0.0.0"]
