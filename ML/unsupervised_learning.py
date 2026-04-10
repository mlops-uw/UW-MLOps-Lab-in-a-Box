import pandas as pd
import matplotlib.pyplot as plt
import argparse
import json
from pathlib import Path
import glob
import os

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


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


def prepare_features(df: pd.DataFrame, sample_size: int = 50000):
    features = ['trip_distance', 'trip_duration_min', 'pickup_hour', 'passenger_count', 'fare_amount']

    missing = [col for col in features if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in preprocessed dataset: {missing}")

    if len(df) > sample_size:
        df = df.sample(n=sample_size, random_state=42)
        print(f"Sampled {sample_size} rows for faster clustering")
    else:
        print(f"Using full dataset with {len(df)} rows")

    X = df[features].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return df, X, X_scaled, features


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


def save_results(metrics: dict, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    with open(output_path / "unsupervised_metrics.json", "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"Saved metrics to {output_path / 'unsupervised_metrics.json'}")


def plot_clusters(df_features, labels, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    plt.figure(figsize=(8, 6))
    plt.scatter(
        df_features['trip_distance'],
        df_features['fare_amount'],
        c=labels,
        s=5,
        alpha=0.4
    )
    plt.xlabel("Trip Distance")
    plt.ylabel("Fare Amount")
    plt.title("KMeans Clusters: Trip Distance vs Fare Amount")
    plt.tight_layout()
    plt.savefig(output_path / "unsupervised_clusters.png", dpi=150)
    plt.close()

    print(f"Saved plot to {output_path / 'unsupervised_clusters.png'}")


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


def main():
    parser = argparse.ArgumentParser(description="Run unsupervised learning on preprocessed taxi data")
    parser.add_argument("--data-path", type=str, required=True, help="Path to preprocessed data")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Directory for results")
    parser.add_argument("--n-clusters", type=int, default=5, help="Number of clusters for final KMeans model")
    parser.add_argument("--max-k", type=int, default=8, help="Maximum k for elbow method")
    parser.add_argument("--sample-size", type=int, default=50000, help="Sample size for faster clustering")

    args = parser.parse_args()

    df = load_data(args.data_path)
    df_sampled, df_features, X_scaled, features = prepare_features(df, sample_size=args.sample_size)

    k_values, inertias = compute_elbow(X_scaled, max_k=args.max_k)
    plot_elbow(k_values, inertias, args.output_dir)

    model, labels = train_kmeans(X_scaled, args.n_clusters)

    metrics = {
        "model": "KMeans",
        "n_clusters": args.n_clusters,
        "inertia": float(model.inertia_),
        "features_used": features,
        "sample_size_used": len(df_sampled),
        "elbow_k_values": k_values,
        "elbow_inertias": [float(x) for x in inertias]
    }

    save_results(metrics, args.output_dir)
    plot_clusters(df_features, labels, args.output_dir)

    print("Unsupervised learning completed successfully")


if __name__ == "__main__":
    main()