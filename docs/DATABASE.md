**This doc contains details about database components of this repo.**

# ClickHouse
Create ClickHouse dirs and change the ownership of the mounted dirs:
```bash
sudo mkdir -p build/.mnt/clickhouse/{data,users,log}
# sudo chown -R $(id -u):$(id -g) build/.mnt/clickhouse
```
See `build/clickhouse/.mnt/users/app-inserter.example.xml` and rename the file.

Download ClickHouse binary if not already.

Docker stuff
```bash
# Start ClickHouse
docker compose -f build/clickhouse.docker-compose.yaml up --force-recreate -d

# Shutdown ClickHouse
docker compose -f build/clickhouse.docker-compose.yaml down -v
```

Test connection
```bash
# Curl
curl -u app_inserter:ChangeMe123 "http://TAILSCALE_IP:8123/?query=SELECT+1"

# Access container shell
docker exec -it ch-server bash

# Interactive SQL shell
docker exec -it ch-server clickhouse-client

# This may not work in some cases due to hostname issues
docker exec -it ch-server clickhouse-client \
    --host=TAILSCALE_IP \
    --port=9000 \
    --user=app_inserter \
    --password=ChangeMe123

# If we have clickhouse-client
clickhouse-client --host TAILSCALE_IP --port 49000 -u app_inserter --password ChangeMe123
```
