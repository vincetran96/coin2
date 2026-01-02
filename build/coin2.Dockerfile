FROM python:3.11.9

USER root

WORKDIR /opt/coin2
COPY . /opt/coin2

RUN apt-get update -y
RUN apt-get install -y iputils-ping dnsutils telnet nano

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

# uv things
ENV PATH="${PATH}:/root/.local/bin"
RUN uv sync
ENV PATH="${PATH}:/opt/coin2/.venv/bin"

# Dagster things
ENV DAGSTER_HOME=/opt/coin2/dagster_src
