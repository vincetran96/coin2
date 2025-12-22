**This doc contains details about catalog components of this repo.**

# Iceberg
Create ClickHouse dirs and change the ownership of the mounted dirs:
```bash
# CREATE A TABLE
./scripts/uv-run-module-with-env.sh app.etl.ohlcv.binance.brz.raw_to_brz_init

# DROP A TABLE
./scripts/uv-run-module-with-env.sh scripts.py.catalog.drop_table \
  --namespace binance \
  --table ohlcv_brz
```
