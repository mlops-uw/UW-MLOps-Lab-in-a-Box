import pandas as pd
import matplotlib.pyplot as plt
import argparse
import json
from pathlib import Path
import glob
import os

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


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


def prepare_features(df: pd.DataFrame):
    features = ['trip_distance', 'trip_duration_min', 'pickup_hour', 'passenger_count', 'fare_amount']

    missing = [col for col in features if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns in preprocessed dataset: {missing}")

    X = df[features]

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X, X_scaled, features


def train_kmeans(X_scaled, n_clusters: int = 5):
    model = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = model.fit_predict(X_scaled)
    return model, labels


def evaluate_clustering(X_scaled, labels):
    score = silhouette_score(X_scaled, labels)
    print(f"Silhouette Score: {score:.4f}")
    return score


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
    plt.scatter(df_features['trip_distance'], df_features['fare_amount'], c=labels, s=5, alpha=0.4)
    plt.xlabel("Trip Distance")
    plt.ylabel("Fare Amount")
    plt.title("KMeans Clusters: Trip Distance vs Fare Amount")
    plt.tight_layout()
    plt.savefig(output_path / "unsupervised_clusters.png", dpi=150)
    plt.close()

    print(f"Saved plot to {output_path / 'unsupervised_clusters.png'}")


def main():
    parser = argparse.ArgumentParser(description="Run unsupervised learning on preprocessed taxi data")
    parser.add_argument("--data-path", type=str, required=True, help="Path to preprocessed data")
    parser.add_argument("--output-dir", type=str, default="outputs", help="Directory for results")
    parser.add_argument("--n-clusters", type=int, default=5, help="Number of clusters")

    args = parser.parse_args()

    df = load_data(args.data_path)
    df_features, X_scaled, features = prepare_features(df)

    model, labels = train_kmeans(X_scaled, args.n_clusters)
    silhouette = evaluate_clustering(X_scaled, labels)

    metrics = {
        "model": "KMeans",
        "n_clusters": args.n_clusters,
        "silhouette_score": silhouette,
        "features_used": features
    }

    save_results(metrics, args.output_dir)
    plot_clusters(df_features, labels, args.output_dir)

    print("Unsupervised learning completed successfully")


if __name__ == "__main__":
    main()