**This doc contains details about debugging components of this repo.**

# Kafka
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

# Coin app
```bash
KAFKA_BOOTSTRAP_SERVER=TAILSCAL_IP:9094 uv run -m app.etl.raw_cli -t ws-binance --output_dir temp
```
