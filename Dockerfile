#FROM alpine:3.5
FROM python:3.7.13-slim
#RUN apk add --update python py-pip
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt
COPY main.py /src/
COPY buzz /src/buzz
COPY modules /src/modules
COPY civil-hash.json /src/key/
CMD python /src/main.py
