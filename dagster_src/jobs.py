from dagster import AssetKey, AssetSelection, define_asset_job

from dagster_src.consts import BINANCE_OHLCV_BRZ_MAX_RUNTIME


# Attach a tag to all runs of this job so you can enforce global concurrency in Dagster instance config
BINANCE_OHLCV_BRZ_CONCURR_TAG = {"concurrency_group": "binance_ohlcv_brz_cc_gr"}
BINANCE_OHLCV_SLV_CONCURR_TAG = {"concurrency_group": "binance_ohlcv_slv_cc_gr"}


binance_ohlcv_job = define_asset_job(
    name="binance_ohlcv_job",
    selection=AssetSelection.keys(
        AssetKey(["binance_ohlcv_brz"]),
        AssetKey(["binance_ohlcv_slv"]),
        AssetKey(["binance_ohlcv_clickhouse"]),
    ),
)

binance_ohlcv_brz_job = define_asset_job(
    name="binance_ohlcv_brz_job",
    selection=AssetSelection.keys(AssetKey(["binance_ohlcv_brz"])),

    # Default config for this job, regardless of how it's triggered (schedule/manual/sensor)
    config={
        "ops": {
            "binance_ohlcv_brz": {"config": {"max_runtime": BINANCE_OHLCV_BRZ_MAX_RUNTIME}},
        }
    },

    tags=BINANCE_OHLCV_BRZ_CONCURR_TAG,
)

binance_ohlcv_slv_ch_job = define_asset_job(
    name="binance_ohlcv_slv_ch_job",
    selection=AssetSelection.keys(
        AssetKey(["binance_ohlcv_slv"]), AssetKey(["binance_ohlcv_clickhouse"]) 
    ),
    tags=BINANCE_OHLCV_SLV_CONCURR_TAG,
)
