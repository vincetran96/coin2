#! /usr/bin/env bash
set -eo pipefail

python -m app.fetch.admin

kubectl apply \
    -f k8s/coin2-init-hb.yaml \
    -f k8s/coin2-fetch-binance.yaml \
    -f k8s/coin2-insert-binance.yaml \
    -f k8s/coin2-pvc.yaml
