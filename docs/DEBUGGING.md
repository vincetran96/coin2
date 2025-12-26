**This doc contains details about debugging components of this repo.**

# Docker
```bash
# Recreate container of a component
docker compose -f build/kafka.docker-compose.yaml up -d kafka-connect

# Full rebuild after image change
docker compose -f build/kafka.docker-compose.yaml up -d --force-recreate kafka-connect

# Stop a service
docker compose -f build/kafka.docker-compose.yaml down kafka-connect

# Stop a service with its volume
docker compose -f build/kafka.docker-compose.yaml down kafka-connect -v

# List environment variables of a container
docker exec -it kafka-connect env
```
