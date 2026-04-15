# ---------------------------
# Monitoring & Observability
# NYC Taxi MLOps - Boeing x WIC x UW
# ---------------------------
# Reads outputs from supervised_learning.py and unsupervised_learning.py,
# logs all metrics to MLflow (Azure ML native), checks for data drift,
# flags performance regressions, and saves a monitoring report.

import argparse
import json
import os
import glob
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import mlflow

warnings.filterwarnings("ignore")


# ---------------------------
# Thresholds (tune as needed)
# ---------------------------
THRESHOLDS = {
    "ridge_r2_min": 0.70,       # Alert if Ridge R2 drops below this
    "ridge_mae_max": 5.00,      # Alert if Ridge MAE exceeds $5
    "ridge_rmse_max": 8.00,     # Alert if Ridge RMSE exceeds $8
    "drift_psi_warn": 0.10,     # PSI warning threshold
    "drift_psi_alert": 0.25,    # PSI alert threshold (industry standard)
}


# ---------------------------
# Load Results from Prior Steps
# ---------------------------
def load_supervised_metrics(supervised_output_dir: str) -> dict:
    path = Path(supervised_output_dir) / "supervised_metrics.json"
    if not path.exists():
        raise FileNotFoundError(f"supervised_metrics.json not found at {path}")
    with open(path) as f:
        return json.load(f)


def load_unsupervised_metrics(unsupervised_output_dir: str) -> dict:
    path = Path(unsupervised_output_dir) / "unsupervised_metrics.json"
    if not path.exists():
        raise FileNotFoundError(f"unsupervised_metrics.json not found at {path}")
    with open(path) as f:
        return json.load(f)


def load_data(data_path: str) -> pd.DataFrame:
    if os.path.isdir(data_path):
        files = glob.glob(os.path.join(data_path, "*.parquet"))
    else:
        files = [data_path] if data_path.endswith(".parquet") else []
    if not files:
        raise ValueError(f"No parquet files found in {data_path}")
    df = pd.concat((pd.read_parquet(f) for f in files), ignore_index=True)
    print(f"Loaded data for drift check: {df.shape}")
    return df


# ---------------------------
# Log Metrics to MLflow
# ---------------------------
def log_to_mlflow(supervised_metrics: dict, unsupervised_metrics: dict):
    print("\n=== Logging metrics to MLflow ===")
    with mlflow.start_run(run_name="monitoring_report", nested=True):

        # --- Supervised: Linear Regression ---
        lr = supervised_metrics.get("linear_regression", {})
        mlflow.log_metric("lr_r2_score",  lr.get("r2_score", 0))
        mlflow.log_metric("lr_mae",       lr.get("mae", 0))
        mlflow.log_metric("lr_rmse",      lr.get("rmse", 0))

        # --- Supervised: Ridge Regression ---
        ridge = supervised_metrics.get("ridge_regression", {})
        mlflow.log_metric("ridge_r2_score", ridge.get("r2_score", 0))
        mlflow.log_metric("ridge_mae",      ridge.get("mae", 0))
        mlflow.log_metric("ridge_rmse",     ridge.get("rmse", 0))

        # --- Unsupervised: KMeans ---
        mlflow.log_metric("kmeans_inertia",   unsupervised_metrics.get("inertia", 0))
        mlflow.log_metric("kmeans_n_clusters", unsupervised_metrics.get("n_clusters", 0))
        mlflow.log_metric("kmeans_num_zones", unsupervised_metrics.get("num_zones", 0))

        # --- Log thresholds as params for traceability ---
        for k, v in THRESHOLDS.items():
            mlflow.log_param(f"threshold_{k}", v)

    print("MLflow logging complete.")


# ---------------------------
# Performance Regression Check
# ---------------------------
def check_performance(supervised_metrics: dict) -> list:
    alerts = []
    ridge = supervised_metrics.get("ridge_regression", {})

    r2 = ridge.get("r2_score", 0)
    mae = ridge.get("mae", 999)
    rmse = ridge.get("rmse", 999)

    if r2 < THRESHOLDS["ridge_r2_min"]:
        alerts.append(f"ALERT: Ridge R2={r2:.4f} is below threshold {THRESHOLDS['ridge_r2_min']}")
    if mae > THRESHOLDS["ridge_mae_max"]:
        alerts.append(f"ALERT: Ridge MAE=${mae:.2f} exceeds threshold ${THRESHOLDS['ridge_mae_max']}")
    if rmse > THRESHOLDS["ridge_rmse_max"]:
        alerts.append(f"ALERT: Ridge RMSE=${rmse:.2f} exceeds threshold ${THRESHOLDS['ridge_rmse_max']}")

    if not alerts:
        print("Performance check PASSED: All metrics within thresholds.")
    else:
        for a in alerts:
            print(a)

    return alerts


# ---------------------------
# Data Drift Check (PSI)
# Population Stability Index on key features
# ---------------------------
def compute_psi(expected: np.ndarray, actual: np.ndarray, bins: int = 10) -> float:
    """Compute PSI between two distributions using quantile-based binning.
    PSI < 0.1 = stable, 0.1-0.25 = warning, >0.25 = significant drift.
    """
    # Use quantile-based bin edges from the expected (baseline) distribution
    # to avoid empty bins and produce more reliable PSI values
    bin_edges = np.unique(np.percentile(expected, np.linspace(0, 100, bins + 1)))

    # Fall back to equal-width if quantiles collapse (e.g. constant feature)
    if len(bin_edges) < 3:
        min_val = min(expected.min(), actual.min())
        max_val = max(expected.max(), actual.max())
        if min_val == max_val:
            return 0.0
        bin_edges = np.linspace(min_val, max_val, bins + 1)

    exp_counts, _ = np.histogram(expected, bins=bin_edges)
    act_counts, _ = np.histogram(actual, bins=bin_edges)

    # Avoid division by zero with small epsilon smoothing
    exp_pct = (exp_counts + 1e-6) / len(expected)
    act_pct = (act_counts + 1e-6) / len(actual)

    psi = np.sum((act_pct - exp_pct) * np.log(act_pct / exp_pct))
    return float(psi)


def check_data_drift(df: pd.DataFrame, output_dir: str) -> dict:
    """
    Simulate drift check by splitting the dataset in half (first half = baseline,
    second half = current). In production, replace baseline with a stored reference.
    """
    print("\n=== Data Drift Check (PSI) ===")
    features = ["trip_distance", "fare_amount", "passenger_count"]
    available = [f for f in features if f in df.columns]

    if not available:
        print("No drift features found in data, skipping drift check.")
        return {}

    mid = len(df) // 2
    baseline = df.iloc[:mid]
    current = df.iloc[mid:]

    drift_results = {}
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, len(available), figsize=(5 * len(available), 4))
    if len(available) == 1:
        axes = [axes]

    for i, feat in enumerate(available):
        psi = compute_psi(baseline[feat].dropna().values, current[feat].dropna().values)
        drift_results[feat] = psi

        if psi >= THRESHOLDS["drift_psi_alert"]:
            status = "DRIFT DETECTED"
        elif psi >= THRESHOLDS["drift_psi_warn"]:
            status = "WARNING"
        else:
            status = "STABLE"

        print(f"  {feat}: PSI={psi:.4f} -> {status}")

        # Plot distributions
        axes[i].hist(baseline[feat].dropna(), bins=40, alpha=0.5, label="Baseline", color="steelblue")
        axes[i].hist(current[feat].dropna(),  bins=40, alpha=0.5, label="Current",  color="orange")
        axes[i].set_title(f"{feat}\nPSI={psi:.4f} ({status})")
        axes[i].set_xlabel(feat)
        axes[i].legend()

    plt.tight_layout()
    plt.savefig(output_path / "drift_report.png", dpi=150)
    plt.close()
    print(f"Drift plot saved to {output_path / 'drift_report.png'}")

    # Log PSI values to MLflow
    with mlflow.start_run(run_name="drift_check", nested=True):
        for feat, psi in drift_results.items():
            mlflow.log_metric(f"psi_{feat}", psi)

    return drift_results


# ---------------------------
# Save Monitoring Report
# ---------------------------
def save_report(
    supervised_metrics: dict,
    unsupervised_metrics: dict,
    drift_results: dict,
    alerts: list,
    output_dir: str,
):
    report = {
        "supervised": supervised_metrics,
        "unsupervised": unsupervised_metrics,
        "drift_psi": drift_results,
        "performance_alerts": alerts,
        "overall_status": "FAIL" if alerts else "PASS",
    }

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    report_path = output_path / "monitoring_report.json"

    with open(report_path, "w") as f:
        json.dump(report, f, indent=2)

    print(f"\nMonitoring report saved to {report_path}")
    print(f"Overall status: {report['overall_status']}")
    return report


# ---------------------------
# Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Monitoring & Observability for NYC Taxi MLOps")
    parser.add_argument("--data-path",              type=str, required=True,  help="Path to preprocessed data (for drift check)")
    parser.add_argument("--supervised-output-dir",  type=str, required=True,  help="Output dir from supervised_learning.py")
    parser.add_argument("--unsupervised-output-dir",type=str, required=True,  help="Output dir from unsupervised_learning.py")
    parser.add_argument("--output-dir",             type=str, default="outputs/monitoring", help="Where to save monitoring outputs")
    args = parser.parse_args()

    print("=" * 50)
    print("  MLOps Monitoring & Observability Step")
    print("=" * 50)

    # Load results from prior pipeline steps
    supervised_metrics   = load_supervised_metrics(args.supervised_output_dir)
    unsupervised_metrics = load_unsupervised_metrics(args.unsupervised_output_dir)

    # Log everything to MLflow / Azure ML
    log_to_mlflow(supervised_metrics, unsupervised_metrics)

    # Check model performance against thresholds
    alerts = check_performance(supervised_metrics)

    # Check for data drift
    df = load_data(args.data_path)
    drift_results = check_data_drift(df, args.output_dir)

    # Save full report
    report = save_report(
        supervised_metrics,
        unsupervised_metrics,
        drift_results,
        alerts,
        args.output_dir,
    )

    print("\nMonitoring completed successfully.")

    # Exit with non-zero if there are critical alerts (will fail the pipeline step)
    if report["overall_status"] == "FAIL":
        print("WARNING: Performance alerts detected. Review monitoring_report.json.")


if __name__ == "__main__":
    main()
