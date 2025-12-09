**This doc contains details about debugging components of this repo.**

# Kafka
```bash
# List topics
docker run -it --rm --network=host apache/kafka:3.9.1 \
    kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --list

# Delete a topic
docker run -it --rm --network=host apache/kafka:3.9.1 \
    kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --delete \
    --topic TOPIC

# Consume from a topic
docker run -it --rm --network=host apache/kafka:3.9.1 \
    kafka-console-consumer.sh \
    --bootstrap-server localhost:9094 \
    --topic TOPIC \
    --from-beginning \
    --property "parse.key=true"

# Describe a topic
docker run -it --rm --network=host apache/kafka:3.9.1 \
    kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --describe \
    --topic TOPIC

# Check access rights
docker run -it --rm --network=host apache/kafka:3.9.1 \
    kafka-acls.sh \
    --bootstrap-server localhost:9094 \
    --list \
    --topic TOPIC

# Reset offset
./bin/kafka/bin/kafka-consumer-groups.sh --bootstrap-server localhost:9094 --group inserter-consumer --reset-offsets --to-earliest --all-topics --execute
```