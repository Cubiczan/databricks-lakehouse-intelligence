# Databricks notebook source
# Silver Layer - Clean, Deduplicate, Validate
import logging

from pyspark.sql.functions import *
from pyspark.sql.window import Window
from delta.tables import DeltaTable
from cubiczan_resilience import resilient

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("silver_transform")

CATALOG = "workspace"
logger.info("Silver Layer - Transformations")


@resilient(timeout=300, max_attempts=3)
def upsert_delta(df, fqn: str, keys: list[str]) -> None:
    """Idempotent MERGE upsert with structured logging and error context.

    Replaces createOrReplace (which wipes the table every run) so the silver
    layer is durable and re-runs are idempotent.
    """
    try:
        if not spark.catalog.tableExists(fqn):
            df.writeTo(fqn).using("delta").createOrReplace()
            logger.info("%s: created with %d rows", fqn, df.count())
            return

        target = DeltaTable.forName(spark, fqn)
        cond = " AND ".join(f"t.{k} = s.{k}" for k in keys)
        (
            target.alias("t")
            .merge(df.alias("s"), cond)
            .whenMatchedUpdateAll()
            .whenNotMatchedInsertAll()
            .execute()
        )
        logger.info("%s: merged %d rows", fqn, df.count())
    except Exception:
        logger.exception("Failed writing %s", fqn)
        raise


df_m = spark.read.table(f"{CATALOG}.lakehouse_bronze.mining_companies")


def dedup_retention(df_raw, df_kept) -> float:
    """Computed silver quality_score: share of source rows kept after dedup (0-1).

    Replaces the earlier hardcoded quality_score literals (lit(0.95), lit(0.92),
    lit(0.90)) — decorative constants claiming to be measures. The ratio is
    computed from the actual dedup outcome on every run.
    """
    total = df_raw.count()
    kept = df_kept.count()
    return round(kept / total, 4) if total else 1.0


df_ms = df_m.dropDuplicates(["company_id"])
quality_companies = dedup_retention(df_m, df_ms)
df_ms = df_ms.withColumn("quality_score", lit(quality_companies)).withColumn("silver_ts", current_timestamp()).drop("ingestion_ts")
upsert_delta(df_ms, f"{CATALOG}.lakehouse_silver.mining_companies", ["company_id"])

df_p = spark.read.table(f"{CATALOG}.lakehouse_bronze.production_records")
w = Window.partitionBy("company_id","commodity","year","quarter")
df_ps = df_p.withColumn("rn",row_number().over(w.orderBy("ingestion_ts"))).filter(col("rn")==1).drop("rn")
quality_production = dedup_retention(df_p, df_ps)
df_ps = df_ps.withColumn("period",concat(col("year"),lit("Q"),col("quarter"))).withColumn("aisc_band",when(col("aisc_usd_per_t")<3500,"Low Cost").when(col("aisc_usd_per_t")<5000,"Mid Cost").otherwise("High Cost")).withColumn("quality_score",lit(quality_production)).withColumn("silver_ts",current_timestamp()).drop("ingestion_ts")
upsert_delta(df_ps, f"{CATALOG}.lakehouse_silver.production_records", ["company_id","commodity","year","quarter"])

df_f = spark.read.table(f"{CATALOG}.lakehouse_bronze.financial_metrics")
w2 = Window.partitionBy("company_id","year","quarter")
df_fs = df_f.withColumn("rn",row_number().over(w2.orderBy("ingestion_ts"))).filter(col("rn")==1).drop("rn")
quality_financials = dedup_retention(df_f, df_fs)
df_fs = df_fs.withColumn("period",concat(col("year"),lit("Q"),col("quarter"))).withColumn("ebitda_margin",round(col("ebitda_m_usd")/col("revenue_m_usd")*100,2)).withColumn("net_margin",round(col("net_income_m_usd")/col("revenue_m_usd")*100,2)).withColumn("quality_score",lit(quality_financials)).withColumn("silver_ts",current_timestamp()).drop("ingestion_ts")
upsert_delta(df_fs, f"{CATALOG}.lakehouse_silver.financial_metrics", ["company_id","year","quarter"])

logger.info("Silver layer complete: 3 tables with computed dedup-retention quality scores")
