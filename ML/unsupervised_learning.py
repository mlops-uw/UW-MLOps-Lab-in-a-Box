# Zone Segmentation by Fare Behavior

import pandas as pd
import matplotlib.pyplot as plt
import argparse
import json
from pathlib import Path
import glob
import os
import joblib

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# ---------------------------
# Load Data
# ---------------------------
def load_data(data_path: str) -> pd.DataFrame:
    print(f"Loading preprocessed data from {data_path}")

    if os.path.isdir(data_path):
        parquet_files = glob.glob(os.path.join(data_path, "*.parquet"))
    else:
        parquet_files = [data_path] if data_path.endswith(".parquet") else []

    if not parquet_files:
        raise ValueError(f"No parquet files found in {data_path}")

    df = pd.concat(
        (pd.read_parquet(file) for file in parquet_files),
        ignore_index=True
    )

    print(f"Loaded data shape: {df.shape}")
    print("Columns:", df.columns.tolist())
    return df


# ---------------------------
# Prepare Features (ZONE LEVEL)
# ---------------------------
def prepare_features(df: pd.DataFrame):
    # Ensure pickup_hour exists
    if 'pickup_hour' not in df.columns:
        df['pickup_hour'] = pd.to_datetime(df['tpep_pickup_datetime']).dt.hour

    # Aggregate by drop-off zone
    zone_df = df.groupby('DOLocationID').agg({
        'fare_amount': 'mean',
        'trip_distance': 'mean',
        'passenger_count': 'mean',
        'pickup_hour': 'mean',
        'DOLocationID': 'count'
    }).rename(columns={
        'DOLocationID': 'trip_count'
    }).reset_index()

    print("Zone-level dataset shape:", zone_df.shape)

    features = [
        'fare_amount',
        'trip_distance',
        'passenger_count',
        'pickup_hour',
        'trip_count'
    ]

    X = zone_df[features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return zone_df, X_scaled, features


# ---------------------------
# Train KMeans
# ---------------------------
def train_kmeans(X_scaled, n_clusters: int = 5):
    print(f"Training KMeans with k={n_clusters}")
    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10,
        max_iter=100
    )
    labels = model.fit_predict(X_scaled)
    print("KMeans training completed")
    return model, labels


# ---------------------------
# Elbow Method
# ---------------------------
def compute_elbow(X_scaled, max_k: int = 8):
    print("Computing elbow curve")
    k_values = list(range(1, max_k + 1))
    inertias = []

    for k in k_values:
        print(f"Running KMeans for k={k}")
        model = KMeans(
            n_clusters=k,
            random_state=42,
            n_init=10,
            max_iter=100
        )
        model.fit(X_scaled)
        inertias.append(model.inertia_)

    return k_values, inertias


# ---------------------------
# Save Results
# ---------------------------
def save_results(metrics: dict, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "unsupervised_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved metrics to {output_path / 'unsupervised_metrics.json'}")


def save_model_artifact(model, output_dir: str, artifact_name: str = "kmeans"):
    output_path = Path(output_dir) / artifact_name
    output_path.mkdir(parents=True, exist_ok=True)
    model_path = output_path / "model.joblib"
    joblib.dump(model, model_path)
    print(f"Saved model artifact to {model_path}")


# ---------------------------
# Plot Clusters (ZONE LEVEL)
# ---------------------------
def plot_clusters(zone_df, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))
    plt.scatter(
        zone_df['trip_count'],
        zone_df['fare_amount'],
        c=zone_df['cluster'],
        s=100,
        alpha=0.7
    )
    plt.xlabel("Trip Count (Demand)")
    plt.ylabel("Average Fare ($)")
    plt.title("Zone Segmentation by Fare Behavior")
    plt.tight_layout()
    plt.savefig(output_path / "zone_clusters.png", dpi=150)
    plt.close()

    print(f"Saved plot to {output_path / 'zone_clusters.png'}")


def plot_clusters_distance(zone_df, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))

    plt.scatter(
        zone_df['trip_distance'],        # X-axis: demand
        zone_df['fare_amount'],     # Y-axis: average trip distance
        c=zone_df['cluster'],
        s=100,
        alpha=0.7
    )

    plt.xlabel("Trip Distance")
    plt.ylabel("Average Trip Fare")
    plt.title("Zone Segmentation by Trip Distance")

    plt.tight_layout()
    plt.savefig(output_path / "zone_clusters_trip_distance.png", dpi=150)
    plt.close()

    print(f"Saved plot to {output_path / 'zone_clusters_trip_distance.png'}")


# ---------------------------
# Plot Elbow Curve
# ---------------------------
def plot_elbow(k_values, inertias, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))
    plt.plot(k_values, inertias, marker='o')
    plt.xlabel("Number of Clusters (k)")
    plt.ylabel("Inertia")
    plt.title("Elbow Method for KMeans")
    plt.tight_layout()
    plt.savefig(output_path / "elbow_curve.png", dpi=150)
    plt.close()

    print(f"Saved elbow plot to {output_path / 'elbow_curve.png'}")


# ---------------------------
# Main
# ---------------------------
def main():
    parser = argparse.ArgumentParser(description="Zone Segmentation using KMeans")
    parser.add_argument("--data-path", type=str, required=True)
    parser.add_argument("--output-dir", type=str, default="outputs")
    parser.add_argument("--n-clusters", type=int, default=5)
    parser.add_argument("--max-k", type=int, default=8)

    args = parser.parse_args()

    # Load data
    df = load_data(args.data_path)

    # Prepare zone-level features
    zone_df, X_scaled, features = prepare_features(df)

    # Elbow method
    k_values, inertias = compute_elbow(X_scaled, args.max_k)
    plot_elbow(k_values, inertias, args.output_dir)

    # Train model
    model, labels = train_kmeans(X_scaled, args.n_clusters)

    # Attach clusters
    zone_df['cluster'] = labels

    # Save zone-level results
    output_path = Path(args.output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    zone_df.to_csv(output_path / "zone_clusters.csv", index=False)

    # Metrics
    metrics = {
        "model": "KMeans",
        "n_clusters": args.n_clusters,
        "inertia": float(model.inertia_),
        "features_used": features,
        "num_zones": len(zone_df),
        "elbow_k_values": k_values,
        "elbow_inertias": [float(x) for x in inertias]
    }

    save_results(metrics, args.output_dir)
    save_model_artifact(model, args.output_dir)

    # Plot clusters
    plot_clusters(zone_df, args.output_dir)
    plot_clusters_distance(zone_df, args.output_dir)

    # Print cluster summary (VERY useful)
    print("\nCluster Summary:")
    print(zone_df.groupby('cluster').mean())

    print("\nUnsupervised learning completed successfully")


if __name__ == "__main__":
    main()
