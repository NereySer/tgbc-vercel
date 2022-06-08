#FROM alpine:3.5
FROM python:3.10-slim
#RUN apk add --update python py-pip

WORKDIR /src

COPY . ./

RUN pip3 install -r requirements.txt && \
    pip3 install gunicorn

CMD gunicorn -b 0.0.0.0:$PORT main:app
