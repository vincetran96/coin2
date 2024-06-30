#! /usr/bin/env bash

kubectl delete \
    -f k8s/coin2-heartbeat.yaml \
    -f k8s/coin2-fetch-binance.yaml \
    -f k8s/coin2-insert-binance.yaml \
    -f k8s/coin2-pvc.yaml
