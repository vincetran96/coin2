FROM python:3.11.9

USER root

WORKDIR /opt/coin2
COPY . /opt/coin2

RUN apt-get update -y
RUN apt-get install -y iputils-ping telnet

RUN pip install -r requirements.txt
