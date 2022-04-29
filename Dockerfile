#FROM alpine:3.5
FROM python:3.7.13-slim
#RUN apk add --update python py-pip

WORKDIR /src

COPY . ./

RUN pwd && ls -la && pip3 install -r requirements.txt

CMD python main.py
