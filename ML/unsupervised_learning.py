"""
Unsupervised Learning - K-Means Clustering for NYC Taxi Trip Patterns
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
import argparse
import json
from pathlib import Path

sns.set_style("whitegrid")


def load_data(data_path: str) -> pd.DataFrame:
    """Load cleaned taxi data"""
    print(f"Loading data from {data_path}")
    df = pd.read_parquet(data_path)
    print(f"Shape: {df.shape}")
    return df


def prepare_features(df: pd.DataFrame, sample_size: int = 100000, random_state: int = 42):
    """Prepare features for clustering"""
    cluster_features = ['PULocationID', 'pickup_hour', 'trip_distance', 'fare_amount']
    
    # Sample for performance
    df_sample = df[cluster_features].sample(n=sample_size, random_state=random_state)
    
    # Normalize features
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(df_sample)
    
    print(f"Sample shape: {df_sample.shape}")
    print("Scaled data ready for clustering")
    print(f"\nMean of scaled features: {X_scaled.mean(axis=0).round(4)}")
    print(f"Std of scaled features: {X_scaled.std(axis=0).round(4)}")
    
    return df_sample, X_scaled, scaler, cluster_features


def elbow_method(X_scaled, k_range=range(2, 11), batch_size: int = 10000):
    """Find optimal K using elbow method"""
    print("\n=== Running Elbow Method ===")
    inertias = []
    
    for k in k_range:
        kmeans = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=batch_size)
        kmeans.fit(X_scaled)
        inertias.append(kmeans.inertia_)
        print(f"K={k}, Inertia={kmeans.inertia_:.0f}")
    
    return list(k_range), inertias


def train_kmeans(X_scaled, n_clusters: int = 4, batch_size: int = 10000):
    """Train K-Means model"""
    print(f"\n=== Training K-Means (K={n_clusters}) ===")
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=batch_size)
    labels = kmeans.fit_predict(X_scaled)
    return kmeans, labels


def analyze_clusters(df_sample, labels, cluster_features):
    """Analyze cluster characteristics"""
    df_sample = df_sample.copy()
    df_sample['cluster'] = labels
    
    print("\n=== Cluster Summary ===")
    cluster_summary = df_sample.groupby('cluster')[cluster_features].mean().round(2)
    print(cluster_summary)
    
    print("\n=== Cluster Sizes ===")
    cluster_sizes = df_sample['cluster'].value_counts().sort_index()
    print(cluster_sizes)
    
    return df_sample, cluster_summary, cluster_sizes


def save_results(k_range, inertias, cluster_summary, cluster_sizes, output_dir: str):
    """Save clustering results"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    results = {
        'elbow_method': {
            'k_values': k_range,
            'inertias': inertias
        },
        'cluster_summary': cluster_summary.to_dict(),
        'cluster_sizes': cluster_sizes.to_dict()
    }
    
    with open(output_path / 'unsupervised_metrics.json', 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n✓ Results saved to {output_path / 'unsupervised_metrics.json'}")


def plot_results(df_sample, k_range, inertias, output_dir: str):
    """Create and save visualizations"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Elbow plot
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.plot(k_range, inertias, marker='o', color='steelblue')
    ax.set_title('Elbow Method - Optimal Number of Clusters')
    ax.set_xlabel('Number of Clusters (K)')
    ax.set_ylabel('Inertia')
    plt.tight_layout()
    plt.savefig(output_path / 'elbow_plot.png', dpi=150)
    print(f"✓ Elbow plot saved to {output_path / 'elbow_plot.png'}")
    plt.close()
    
    # Cluster visualization
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    colors = ['#2196F3', '#FF9800', '#4CAF50', '#E91E63']
    
    # Scatter: pickup hour vs fare
    for c in range(4):
        mask = df_sample['cluster'] == c
        axes[0].scatter(df_sample.loc[mask, 'pickup_hour'],
                        df_sample.loc[mask, 'fare_amount'],
                        alpha=0.3, s=5, c=colors[c], label=f'Cluster {c}')
    axes[0].set_xlabel('Pickup Hour')
    axes[0].set_ylabel('Fare Amount ($)')
    axes[0].set_title('Clusters: Pickup Hour vs Fare')
    axes[0].legend()
    
    # Bar chart: average fare by cluster
    cluster_stats = df_sample.groupby('cluster')['fare_amount'].mean()
    cluster_stats.plot(kind='bar', ax=axes[1], color=colors)
    axes[1].set_title('Average Fare by Cluster')
    axes[1].set_xlabel('Cluster')
    axes[1].set_ylabel('Average Fare ($)')
    axes[1].set_xticklabels([f'C{i}' for i in range(4)], rotation=0)
    
    plt.tight_layout()
    plt.savefig(output_path / 'cluster_visualization.png', dpi=150)
    print(f"✓ Cluster plot saved to {output_path / 'cluster_visualization.png'}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Train unsupervised learning model')
    parser.add_argument('--data-path', type=str, default='data_cleaned/yellow_tripdata_cleaned.parquet',
                        help='Path to cleaned data')
    parser.add_argument('--output-dir', type=str, default='outputs',
                        help='Output directory for results')
    parser.add_argument('--sample-size', type=int, default=100000,
                        help='Sample size for clustering')
    parser.add_argument('--n-clusters', type=int, default=4,
                        help='Number of clusters')
    
    args = parser.parse_args()
    
    # Load and prepare data
    df = load_data(args.data_path)
    df_sample, X_scaled, scaler, cluster_features = prepare_features(
        df, sample_size=args.sample_size
    )
    
    # Elbow method
    k_range, inertias = elbow_method(X_scaled)
    
    # Train K-Means
    kmeans, labels = train_kmeans(X_scaled, n_clusters=args.n_clusters)
    
    # Analyze clusters
    df_sample, cluster_summary, cluster_sizes = analyze_clusters(
        df_sample, labels, cluster_features
    )
    
    # Save results
    save_results(k_range, inertias, cluster_summary, cluster_sizes, args.output_dir)
    
    # Plot results
    plot_results(df_sample, k_range, inertias, args.output_dir)
    
    print("\n✓ Unsupervised learning pipeline completed successfully")


if __name__ == "__main__":
    main()