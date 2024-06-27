# Prerequisites
- Assuming that you're running on Tailscale & K3s


# Components
## App Docker image
```bash
chmod +x build/build.sh
./build/build.sh tag_name
chmod +x build/local-k8s-repo.sh
./build/local-k8s-repo.sh
```
## Kafka
### Setup cluster
```bash
docker compose -f build/kafka.docker-compose.yaml up
```
### Console commands
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
```
### Prometheus
#### UFW config
- Create a file named `/etc/ufw/applications.d/kafka`:
    ```
    [Kafka]
    title=Kafka ports
    description=For access into Kafka Docker
    ports=9200:9204/tcp
    ```
- Run `sudo ufw allow Kafka`
#### Prometheus and Grafana
- https://www.confluent.io/blog/monitor-kafka-clusters-with-prometheus-grafana-and-confluent/
- https://medium.com/@oredata-engineering/setting-up-prometheus-grafana-for-kafka-on-docker-8a692a45966c
- Check the following endpoint for output: http://TAILSCALE_IP:PROMETHEUS_PORT/metrics
#### Service data export configs
**Kafka brokers**
- https://github.com/prometheus/jmx_exporter/blob/release-1.0.1/example_configs/kafka-2_0_0.yml
- https://gist.githubusercontent.com/baturalpk/fb2e394e2d133d107477bb198ab0a92c/raw/a7917c6f633666ee84e1588d663fde48d6dec640/kafka-broker.yml
#### JMX jar execution file
- https://repo.maven.apache.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar
## App k8s deployment
### Configs
```bash
kubectl create ns coin2
kubectl create -f k8s/coin2-configmap.yaml
```
### Start app
```bash
kubectl apply \
    -f k8s/coin2-init-hb.yaml \
    -f k8s/coin2-fetch-binance.yaml \
    -f k8s/coin2-insert-binance.yaml \
    -f k8s/coin2-pvc.yaml
```
