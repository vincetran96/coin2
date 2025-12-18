#! /usr/bin/env bash
set -eo pipefail

MODULE=$1

set -a
source ./build/.env
set +a

# We pass all arguments from position 2 into uv run
# Also, redirect stderr to stdout
uv run -m $MODULE "${@:2}" 2>&1  
