**This doc contains details about orchestration component of this repo.**

# Dagster
```bash
# Start dev server
set -a && source ./build/.env && set +a \
    && DAGSTER_HOME="$PWD/.dagster" \
    dg dev -m dagster_src --host TAILSCALE_IP
```
