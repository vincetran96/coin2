#! /usr/bin/env bash
set -eo pipefail

# Create bridge network
docker network inspect data-infra >/dev/null 2>&1 || docker network create -d bridge data-infra
