**This doc contains details about debugging components of this repo.**

# Docker
```bash
# Recreate container of a component
docker compose -f build/kafka.docker-compose.yaml up -d kafka-connect

# Full rebuild after image change
docker compose -f build/kafka.docker-compose.yaml up -d --force-recreate kafka-connect

# Stop a service
docker compose -f build/kafka.docker-compose.yaml down kafka-connect

# Stop a service with its volume
docker compose -f build/kafka.docker-compose.yaml down kafka-connect -v
```


# Coin app
```bash
# Fetch from binance
KAFKA_BOOTSTRAP_SERVER=TAILSCALE_IP:9094 uv run -m app.fetch.binance

# Save raw data
KAFKA_BOOTSTRAP_SERVER=TAILSCALE_IP:9094 uv run -m app.etl.save_raw_cli -t ws-binance --output_dir temp

# Execute shell inside pod
kubectl exec -n coin2 -it coin2-fetch -- sh
```
