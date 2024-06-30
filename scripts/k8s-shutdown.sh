#! /usr/bin/env bash

kubectl delete \
    -f k8s/coin2-fetch-binance.yaml \
    -f k8s/coin2-insert-binance.yaml \
    -f k8s/coin2-pvc.yaml

docker run -it --rm --network=host bitnami/kafka:3.6.2 \
    kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --delete \
    --topic ws-binance
