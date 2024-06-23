#! /usr/bin/env bash
set -eo pipefail

THIS_SCRIPT_DIR=$(dirname "$0")
PROJECT_ROOT=$(realpath "${THIS_SCRIPT_DIR}/..")
HEARTBEAT_LOGDIR=${PROJECT_ROOT}/logs/app/heartbeat.log

# python -m app.fetch.admin
python -m app.heartbeat
