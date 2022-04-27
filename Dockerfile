#FROM alpine:3.5
FROM python:3.6.15-slim
#RUN apk add --update python py-pip
COPY requirements.txt /src/requirements.txt
RUN pip3 install -r /src/requirements.txt
COPY app.py /src
COPY buzz /src/buzz
CMD python /src/app.py
