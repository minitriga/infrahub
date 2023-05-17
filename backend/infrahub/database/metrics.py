from prometheus_client import Histogram

METRIC_PREFIX = "infrahub_db"

QUERY_EXECUTION_METRICS = Histogram(
    f"{METRIC_PREFIX}_query_execution_seconds",
    "Execution time to query the database",
    labelnames=["type", "query"],
    buckets=[0.005, 0.025, 0.1, 0.5, 1],
)
