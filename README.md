# Kafka
```
docker run -it --rm --network=host bitnami/kafka:3.6.2 \
    kafka-topics.sh \
    --bootstrap-server localhost:9094 \
    --list 

docker run -it --rm --network=host bitnami/kafka:3.6.2 \
    kafka-console-consumer.sh \
    --bootstrap-server localhost:9094 \
    --topic coin2-ws \
    --from-beginning \
    --property "parse.key=true"
```
