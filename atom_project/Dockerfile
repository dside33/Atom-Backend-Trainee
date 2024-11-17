FROM python:3.9-alpine3.16

COPY requirements.txt /temp/requirements.txt

COPY . /usr/src/app
WORKDIR /usr/src/app
EXPOSE 8000

RUN pip install -r /temp/requirements.txt && \
    adduser --disabled-password fastapi-user

USER fastapi-user