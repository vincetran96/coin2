from dagster import DagsterRunStatus, RunRequest, RunsFilter, SkipReason, schedule

from dagster_src.jobs import (
    binance_ohlcv_brz_job,
    binance_ohlcv_slv_ch_job,
    BINANCE_OHLCV_SLV_CONCURR_TAG,
)


@schedule(
    name="binance_ohlcv_brz_20m",
    cron_schedule="*/20 * * * *",
    job=binance_ohlcv_brz_job,
)
def binance_ohlcv_brz_20m(context):
    """Run Raw -> Bronze every 20 minutes

    Overlapping runs are allowed for this schedule.
    """
    # Job default run config lives in `dagster_src/jobs.py` (single source of truth).
    # `run_config` can be used here to override the default config.
    return {}


@schedule(
    name="binance_ohlcv_slv_ch_5m",
    cron_schedule="*/5 * * * *",
    job=binance_ohlcv_slv_ch_job,
)
def binance_ohlcv_slv_ch_5m(context):
    """Run Silver -> ClickHouse every 5 minutes (ClickHouse depends on Silver within the job run)
    """
    active_statuses = [
        DagsterRunStatus.QUEUED,
        DagsterRunStatus.NOT_STARTED,
        DagsterRunStatus.STARTING,
        DagsterRunStatus.STARTED,
        DagsterRunStatus.MANAGED,
        DagsterRunStatus.CANCELING,
    ]
    existing = context.instance.get_runs(
        RunsFilter(job_name="binance_ohlcv_slv_ch", statuses=active_statuses),
        limit=1,
    )
    if existing:
        return SkipReason("Skipping: a prior `binance_ohlcv_slv_ch` job run is still active.")

    return RunRequest(tags=BINANCE_OHLCV_SLV_CONCURR_TAG)
