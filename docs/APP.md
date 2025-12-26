**This doc contains details about app component of this repo.**

# Coin app
```bash
# Fetch from binance
./scripts/uv-run-module-with-env.sh app.fetch.binance

# Save raw data
./scripts/uv-run-module-with-env.sh app.etl.save_raw_cli -t ws-binance --output_dir temp

# ETL Layers
./scripts/uv-run-module-with-env.sh app.etl.ohlcv.binance.raw_to_brz_cli
./scripts/uv-run-module-with-env.sh app.etl.ohlcv.binance.brz_to_slv_daft_cli

# Execute shell inside pod
kubectl exec -n coin2 -it coin2-fetch -- sh

# Execute python module with env variables
./scripts/uv-run-module-with-env.sh app.integration_tests.test_iceberg
```
