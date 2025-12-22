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

# List environment variables of a container
docker exec -it kafka-connect env
```


# Coin app
```bash
# Fetch from binance
./scripts/uv-run-module-with-env.sh app.fetch.binance

# Save raw data
./scripts/uv-run-module-with-env.sh app.etl.save_raw_cli -t ws-binance --output_dir temp

# Consume from Kafka to Bronze
./scripts/uv-run-module-with-env.sh app.etl.ohlcv.binance.raw_to_brz

# Execute shell inside pod
kubectl exec -n coin2 -it coin2-fetch -- sh

# Execute python module with env variables
./scripts/uv-run-module-with-env.sh app.integration_tests.test_iceberg
```
