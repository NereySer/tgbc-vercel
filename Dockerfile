#FROM alpine:3.5
FROM python:3.10-slim
#RUN apk add --update python py-pip

WORKDIR /src

COPY . ./

RUN pip3 install -r requirements.txt

CMD python main.py
