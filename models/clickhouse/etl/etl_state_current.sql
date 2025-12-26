-- Table that stores the state of the ETL processes into ClickHouse
CREATE DATABASE IF NOT EXISTS etl;

CREATE TABLE IF NOT EXISTS etl.etl_state_current
(
    job_name                String,
    source                  String,
    source_identifier       String,  -- Full name to the source table
    dest_identifier         String,  -- Full name to the destination table in ClickHouse
    last__change_tstamp     DateTime64(6, 'UTC'),  -- The last value of the audit column _change_tstamp in this ETL run
    
    -- Audit columns
    _insert_tstamp          DateTime64(6, 'UTC')  DEFAULT now64(6, 'UTC'),  -- Insert timestamp of this record into this table
)
ENGINE = ReplacingMergeTree(_insert_tstamp)
PARTITION BY toYYYYMMDD(_insert_tstamp)
ORDER BY (job_name)
;
