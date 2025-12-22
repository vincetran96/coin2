#!/usr/bin/env bash
set -eo pipefail

# Get env vars
source ./build/.env

CONNECTOR_NAME=${1:-iceberg-binance-ohlcv-brz}
CONTROL_TOPIC=${2:-ctrl-iceberg-ws-binance}
CONSUMER_GROUP=${3:-connect-iceberg-binance-ohlcv-brz}  # Not sure about this

echo "=== Cleaning up Kafka Connect Connector: $CONNECTOR_NAME ==="

# Delete connector
echo "Deleting connector..."
curl -X DELETE "$KAFKA_CONNECT_ENDPOINT/connectors/$CONNECTOR_NAME" 2>/dev/null || echo "Connector not found\n"

# Delete control topic
echo "Deleting control topic..."
./bin/kafka/bin/kafka-topics.sh \
  --bootstrap-server "$KAFKA_BOOTSTRAP_SERVER" \
  --delete \
  --topic "$CONTROL_TOPIC" 2>/dev/null || echo "Topic not found"

# Delete consumer group
echo "Deleting consumer group..."
./bin/kafka/bin/kafka-consumer-groups.sh \
  --bootstrap-server "$KAFKA_BOOTSTRAP_SERVER" \
  --delete \
  --group "$CONSUMER_GROUP" 2>/dev/null || echo "Group not found"

echo "Cleanup complete"
