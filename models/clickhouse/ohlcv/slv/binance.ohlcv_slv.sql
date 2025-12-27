-- Table that mirrors the Binance OHLCV Silver table in Iceberg
CREATE DATABASE IF NOT EXISTS binance;

CREATE TABLE IF NOT EXISTS binance.ohlcv_slv
(
    exchange                   String,
    symbol                     String,
    event_tstamp               DateTime64(3, 'UTC'),

    open                       Nullable(Float64),
    high                       Nullable(Float64),
    low                        Nullable(Float64),
    close                      Nullable(Float64),
    volume                     Nullable(Float64),

    src_change_tstamp          DateTime64(6, 'UTC'),                          -- Change timestamp from the source. This is used as version column: latest wins based on this

    -- Audit columns
    _change_tstamp             DateTime64(6, 'UTC') DEFAULT now64(6, 'UTC'),  -- Insert timestamp of this record into this table
)
ENGINE = ReplacingMergeTree(src_change_tstamp)
PARTITION BY toYYYYMMDD(event_tstamp)
ORDER BY (exchange, symbol, event_tstamp)
;
