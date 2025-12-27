FROM python:3.11.9

USER root

WORKDIR /opt/coin2
COPY . /opt/coin2

RUN apt-get update -y
RUN apt-get install -y iputils-ping dnsutils telnet nano

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

ENV PATH="${PATH}:/root/.local/bin"
RUN uv sync
