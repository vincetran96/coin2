**This doc contains details about debugging components of this repo.**

# Kafka
```bash
# List topics
docker run -it --rm --network=host bitnami/kafka:3.6.2 \
    kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --list

# Delete a topic
docker run -it --rm --network=host bitnami/kafka:3.6.2 \
    kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --delete \
    --topic TOPIC

# Consume from a topic
docker run -it --rm --network=host bitnami/kafka:3.6.2 \
    kafka-console-consumer.sh \
    --bootstrap-server localhost:9094 \
    --topic TOPIC \
    --from-beginning \
    --property "parse.key=true"

# Describe a topic
docker run -it --rm --network=host bitnami/kafka:3.6.2 \
    kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --describe \
    --topic TOPIC

# Check access rights
docker run -it --rm --network=host bitnami/kafka:3.6.2 \
    kafka-acls.sh \
    --bootstrap-server localhost:9094 \
    --list \
    --topic TOPIC
```