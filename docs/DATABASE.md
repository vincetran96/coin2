**This doc contains details about database components of this repo.**

# ClickHouse
Create ClickHouse dirs and change the ownership of the mounted dirs:
```bash
sudo mkdir -p build/.mnt/clickhouse/{data,users,log}
# sudo chown -R $(id -u):$(id -g) build/.mnt/clickhouse
```

Add a file `build/clickhouse/.mnt/users/app-inserter.xml` with this content:
```xml
<clickhouse>
  <users>
    <app_inserter>
      <password>ChangeMe123</password>

      <!-- restrict networks to host/docker bridge; adjust to your LAN/Tailscale as needed -->
      <networks>
        <ip>::/0</ip>
        <!-- <ip>127.0.0.1/32</ip> -->
      </networks>

      <profile>default</profile>
      <quota>default</quota>
    </app_inserter>
  </users>
</clickhouse>
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
