#! /usr/bin/env bash
python -m app.heartbeat &
python -m app.fetch.admin &
