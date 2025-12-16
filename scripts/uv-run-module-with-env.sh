#! /usr/bin/env bash
set -eo pipefail

MODULE=$1

set -a
source ./build/.env
set +a

uv run -m $MODULE
