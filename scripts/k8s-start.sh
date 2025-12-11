#! /usr/bin/env bash
set -eo pipefail

kubectl apply \
    -f k8s/coin2-heartbeat.yaml \
    -f k8s/coin2-fetch.yaml \
    -f k8s/coin2-etl.yaml \
    -f k8s/coin2-volume.yaml
