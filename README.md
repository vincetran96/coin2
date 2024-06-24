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
