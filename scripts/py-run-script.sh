#! /usr/bin/env bash
set -eo pipefail

MODULE=$1

uv run -m $MODULE
