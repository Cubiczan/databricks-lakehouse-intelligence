# Databricks notebook source
# MLflow - Signal Score Experiment Tracking (Serverless Compatible)
#
# Illustrative metrics: the avg/max/min scores logged below are fixed demonstration values
# logged verbatim for each weight configuration — they are NOT computed aggregates
# of the loaded table. Compute per-configuration aggregates from the gold table
# before treating them as measurements.
import mlflow
import pandas as pd
from pyspark.sql.functions import *

CATALOG = "workspace"
mlflow.set_tracking_uri("databricks")
mlflow.set_registry_uri("databricks-uc")
mlflow.set_experiment("/Shared/Lakehouse_Intelligence/experiments/signal_score_v1")

df = spark.read.table(f"{CATALOG}.lakehouse_gold.mining_signal_scores").toPandas()
print(f"Loaded {len(df)} companies")

with mlflow.start_run(run_name="baseline"):
    mlflow.log_param("grade_weight", 0.20)
    mlflow.log_param("cost_weight", 0.25)
    mlflow.log_metric("avg_score", 65.0)
    mlflow.log_metric("max_score", 85.0)
    mlflow.log_metric("min_score", 45.0)
    mlflow.log_metric("num_companies", 10)
    print("  baseline logged OK")

with mlflow.start_run(run_name="cost_focused"):
    mlflow.log_param("grade_weight", 0.15)
    mlflow.log_param("cost_weight", 0.30)
    mlflow.log_metric("avg_score", 63.0)
    mlflow.log_metric("max_score", 82.0)
    mlflow.log_metric("min_score", 42.0)
    mlflow.log_metric("num_companies", 10)
    print("  cost_focused logged OK")

with mlflow.start_run(run_name="growth_focused"):
    mlflow.log_param("grade_weight", 0.25)
    mlflow.log_param("cost_weight", 0.15)
    mlflow.log_metric("avg_score", 67.0)
    mlflow.log_metric("max_score", 88.0)
    mlflow.log_metric("min_score", 44.0)
    mlflow.log_metric("num_companies", 10)
    print("  growth_focused logged OK")

with mlflow.start_run(run_name="esg_focused"):
    mlflow.log_param("grade_weight", 0.20)
    mlflow.log_param("cost_weight", 0.20)
    mlflow.log_metric("avg_score", 64.0)
    mlflow.log_metric("max_score", 83.0)
    mlflow.log_metric("min_score", 43.0)
    mlflow.log_metric("num_companies", 10)
    print("  esg_focused logged OK")

print("MLflow experiments complete.")
