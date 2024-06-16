# Prerequisites
- Assuming that you're running on Tailscale


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
### Commands
```bash
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
## App k8s deployment
### Configs
```bash
kubectl create -f coin2-configmap.yaml
```
