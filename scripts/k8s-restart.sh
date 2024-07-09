#! /usr/bin/env bash
set -eo pipefail

kubectl rollout restart deployment coin2-fetch -n coin2
kubectl rollout restart deployment coin2-insert -n coin2
kubectl rollout restart deployment coin2-heartbeat -n coin2
