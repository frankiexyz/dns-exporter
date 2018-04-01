FROM alpine:latest

MAINTAINER janitor@netops.life

RUN apk update && apk add python3 py3-pip
RUN pip3 install dnspython
COPY ./exporter.py /
EXPOSE 8088
CMD ["python3", "/exporter.py"]
