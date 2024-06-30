#! /usr/bin/env bash
set -eo pipefail

kubectl apply \
    -f k8s/coin2-fetch-binance.yaml \
    -f k8s/coin2-insert-binance.yaml \
    -f k8s/coin2-pvc.yaml
