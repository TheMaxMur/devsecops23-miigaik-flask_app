FROM python:3.11.3-slim-buster

COPY . /app

RUN apt update && \
    apt install libmariadb-dev g++ libpq-dev gcc -y

RUN python3 -m pip install -r /app/requirements.txt

RUN groupadd python && \
    useradd python -g python

RUN chown -R python:python /app

USER python

WORKDIR /app

CMD ["flask", "run", "--host=0.0.0.0"]
