# Prerequisites
- Assuming that we're running on Tailscale & K3s
- Refer to [Ansible README](ansible/README.md)


# Architecture
TODO: Add this.


# Deployment steps
## Environment
Rename the `.env.example` file to `.env` and change the values as appropriate.

## Infra
```bash
chmod +x scripts/data-infra.sh
./scripts/data-infra.sh
```

Docker (optional if not run data-infra.sh)
```bash
docker network create -d bridge data-infra
```
## Kafka
### Setup cluster
Note that the Kafka component depends on the storage component (enabling Kafka Connect to write to storage).
```bash
# This build uses cache
chmod +x build/kafka-connect.build.sh
./build/kafka-connect.build.sh vincetran96/kafka-connect:test

docker compose -f build/kafka.docker-compose.yaml up --force-recreate -d
chmod +x scripts/kafka-init.sh
./scripts/kafka-init.sh
```
### Monitoring with Prometheus and Grafana
#### Prometheus and Grafana resourcess
- https://www.confluent.io/blog/monitor-kafka-clusters-with-prometheus-grafana-and-confluent/
- https://medium.com/@oredata-engineering/setting-up-prometheus-grafana-for-kafka-on-docker-8a692a45966c
#### UFW config
- Create a file named `/etc/ufw/applications.d/kafka`:
  ```
  [Kafka]
  title=Kafka ports
  description=For access into Kafka Docker cluster
  ports=9200:9204/tcp
  ```
- Run `sudo ufw allow Kafka`
#### Service data export config examples
**Option 1. KMinion**
- https://github.com/redpanda-data/kminion/tree/master
- The export port can be 9200, for example.

**Option 2. JMX**
- *Brokers*
  - https://github.com/prometheus/jmx_exporter/blob/release-1.0.1/example_configs/kafka-2_0_0.yml
  - https://gist.githubusercontent.com/baturalpk/fb2e394e2d133d107477bb198ab0a92c/raw/a7917c6f633666ee84e1588d663fde48d6dec640/kafka-broker.yml
- *Jar execution file to export data*
  - https://repo.maven.apache.org/maven2/io/prometheus/jmx/jmx_prometheus_javaagent/0.20.0/jmx_prometheus_javaagent-0.20.0.jar
#### Setup cluster
```bash
docker compose -f build/monitoring.docker-compose.yaml up --force-recreate -d
```
#### After things are up
- Check the following endpoint for output of a service (e.g., KMinion): `http://TAILSCALE_IP:9200/metrics`
- Check the following endpoint for Prometheus datasources' status: `http://TAILSCALE_IP:19090/targets`
  - If the Prometheus data source for Grafana doesn't exist, manually add this: endpoint: `http://prometheus:9090`
- Import dashboards into Grafana from [here](./assets/monitoring/grafana/dashboards/).
## Storage layer
### Resources
- https://blog.min.io/modern-data-architectures-with-iceberg-and-tabular/
```bash
docker compose -f build/minio.docker-compose.yaml up --force-recreate -d
```
## Database
The database can be ClickHouse, etc. To get started, see [DATABASE](docs/DATABASE.md).
- ClickHouse quick commands:
  ```bash
  # To start server
  docker compose -f build/clickhouse.docker-compose.yaml up --force-recreate -d

  # To shutdown server
  docker rm -f ch-db
  ```
## Build Coin app Docker image
```bash
# This build does NOT use cache
chmod +x build/coin2.build.sh
./build/coin2.build.sh vincetran96/coin2:test

chmod +x build/coin2.local-k8s-repo.sh
./build/coin2.local-k8s-repo.sh vincetran96/coin2:test
```
## Deploy Coin app k8s cluster
### K8s configs
```bash
kubectl create ns coin2
kubectl create -f k8s/coin2-configmap.yaml
```
### Update some configs
Update appropriate values in `k8s/coin2-volume.example.yaml` and rename the file.
### Start the app
```bash
kubectl apply \
    -f k8s/coin2-heartbeat.yaml \
    -f k8s/coin2-fetch.yaml \
    -f k8s/coin2-etl.yaml \
    -f k8s/coin2-volume.yaml
```


# Summary of exposed ports
## Kafka
```
9094, 9095, 9096: Kafka brokers
9200: KMinion
60094: Kafka UI
58081, 59203: Kafka schema registry
58083: Kafka Connect
```
## Monitoring
```
59090, 59093: Prometheus
63000: Grafana
```
## Storage
```
59000, 59001: MinIO
58181: Iceberg REST server
```


# Quick scripts
```bash
# Start k8s things
./scripts/k8s-start.sh

# Stop k8s things
./scripts/k8s-shutdown.sh
```


# Debug
Refer to [DEBUGGING](docs/DEBUGGING.md).