**This doc contains details about database components of this repo.**

# Kafka commands
Make sure we have a binary copy of Kafka executables.
```bash
# List topics
./bin/kafka/bin/kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --list

# Delete a topic
./bin/kafka/bin/kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --delete \
    --topic TOPIC

# Consume from a topic
./bin/kafka/bin/kafka-console-consumer.sh \
    --bootstrap-server localhost:9094 \
    --topic TOPIC \
    --from-beginning \
    --property "parse.key=true"

# Describe a topic
./bin/kafka/bin/kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --describe \
    --topic TOPIC

# Check access rights
./bin/kafka/bin/kafka-acls.sh \
    --bootstrap-server localhost:9094 \
    --list \
    --topic TOPIC

# Describe offsets
./bin/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9094 --group inserter-consumer --describe --offsets

# Reset offset
./bin/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9094 --group inserter-consumer --reset-offsets --to-earliest --all-topics --execute
```


# Schema registry
```bash
# List all schemas/subjects
curl -sS 'http://localhost:58081/subjects' | jq

# Show the latest schema of an object
curl -sS "http://localhost:58081/subjects/binance_ws-value/versions/latest" | jq

# Show all subjects with their latest schema (compact):
curl -sS 'http://localhost:58081/subjects' | jq -r '.[]' | while read s; do
  echo "=== $s ==="
  curl -sS "http://localhost:58081/subjects/$s/versions/latest" | jq
done
```


# Kafka Connect
```bash
# Show information about a connector
curl -s http://localhost:58083/connectors/iceberg-binance-ohlcv-brz/status | jq

# Delete a connector config
curl -X DELETE http://localhost:58083/connectors/iceberg-binance-ohlcv-brz

# Restart a connector
curl -X POST http://localhost:58083/connectors/iceberg-binance-ohlcv-brz/restart
```
