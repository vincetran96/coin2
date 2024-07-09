FROM python:3.11.9

USER root

WORKDIR /opt/coin2
COPY . /opt/coin2

RUN apt-get update -y
RUN apt-get install -y iputils-ping telnet nano pipx

ENV PATH="${PATH}:/root/.local/bin"
RUN pipx install poetry
RUN poetry self add poetry-plugin-export
RUN poetry export -f requirements.txt --output requirements.txt
RUN pip install -r requirements.txt
