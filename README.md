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
docker compose -f build/kafka.docker-compose.yaml up --force-recreate
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
#### Service data export config examples
**Kafka**

**1. KMinion**
- https://github.com/redpanda-data/kminion/tree/master

**2. JMX**
- *Brokers*
  - https://github.com/prometheus/jmx_exporter/blob/release-1.0.1/example_configs/kafka-2_0_0.yml
  - https://gist.githubusercontent.com/baturalpk/fb2e394e2d133d107477bb198ab0a92c/raw/a7917c6f633666ee84e1588d663fde48d6dec640/kafka-broker.yml
- *Jar execution file to export data*
  - https://repo.maven.apache.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar
#### After things are up
- Check the following endpoint for output of a service: `http://TAILSCALE_IP:EXPORT_PORT/metrics`
- Check the following endpoint for Prometheus datasources' status: `http://TAILSCALE_IP:9090/targets`
## App k8s deployment
### Configs
```bash
kubectl create ns coin2
kubectl create -f k8s/coin2-configmap.yaml
```
### Start app
```bash
kubectl apply \
    -f k8s/coin2-heartbeat.yaml \
    -f k8s/coin2-fetch.yaml \
    -f k8s/coin2-insert.yaml \
    -f k8s/coin2-pvc.yaml
```


# Debugging
```bash
# Start k8s things
./scripts/k8s-start.sh

# Stop k8s things
./scripts/k8s-shutdown.sh
```
