"""
Supervised Learning - Linear Regression for NYC Taxi Fare Prediction
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import argparse
import json
from pathlib import Path
import glob
import os

sns.set_style("whitegrid")


def load_data(data_path: str) -> pd.DataFrame:
    """Load cleaned taxi data"""
    print(f"Loading data from {data_path}")
    
    # Get all parquet files in the folder
    parquet_files = glob.glob(os.path.join(data_path, "*.parquet"))
    
    if not parquet_files:
        raise ValueError(f"No parquet files found in {data_path}")
    
    print(f"Found {len(parquet_files)} parquet files")
    
    # Read and combine all parquet files
    df = pd.concat(
        (pd.read_parquet(file) for file in parquet_files),
        ignore_index=True
    )
    
    print(f"Final shape: {df.shape}")
    
    return df


def prepare_features(df: pd.DataFrame, test_size: float = 0.2, random_state: int = 42):
    """Prepare features and split data"""
    features = ['trip_distance', 'trip_duration_min', 'pickup_hour', 'passenger_count']
    target = 'fare_amount'
    
    X = df[features]
    y = df[target]
    
    # Train-test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    
    # Normalize features
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    print(f"Training set: {X_train.shape[0]:,} rows")
    print(f"Test set: {X_test.shape[0]:,} rows")
    
    return X_train_scaled, X_test_scaled, y_train, y_test, scaler, features


def train_linear_regression(X_train, y_train):
    """Train Linear Regression model"""
    print("\n=== Training Linear Regression (No Regularization) ===")
    model = LinearRegression()
    model.fit(X_train, y_train)
    return model


def train_ridge_regression(X_train, y_train, alpha: float = 1.0):
    """Train Ridge Regression model"""
    print(f"\n=== Training Ridge Regression (alpha={alpha}) ===")
    model = Ridge(alpha=alpha, random_state=42)
    model.fit(X_train, y_train)
    return model


def evaluate_model(model, X_test, y_test, model_name: str):
    """Evaluate model and return metrics"""
    y_pred = model.predict(X_test)
    
    metrics = {
        'model': model_name,
        'r2_score': r2_score(y_test, y_pred),
        'mae': mean_absolute_error(y_test, y_pred),
        'rmse': np.sqrt(mean_squared_error(y_test, y_pred))
    }
    
    print(f"\n=== {model_name} Results ===")
    print(f"R² Score:           {metrics['r2_score']:.4f}")
    print(f"Mean Absolute Error: ${metrics['mae']:.2f}")
    print(f"Root Mean Sq Error:  ${metrics['rmse']:.2f}")
    
    return metrics, y_pred


def save_results(metrics: dict, output_dir: str):
    """Save metrics to JSON"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    with open(output_path / 'supervised_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=2)
    
    print(f"\n✓ Metrics saved to {output_path / 'supervised_metrics.json'}")


def plot_results(y_test, y_pred, output_dir: str):
    """Create and save visualization"""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    
    # Sample for visualization
    sample_size = min(5000, len(y_test))
    indices = np.random.choice(len(y_test), sample_size, replace=False)
    y_test_sample = y_test.iloc[indices]
    y_pred_sample = y_pred[indices]
    
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Actual vs Predicted
    axes[0].scatter(y_test_sample, y_pred_sample, alpha=0.3, s=5)
    axes[0].plot([0, 100], [0, 100], 'r--', label='Perfect prediction')
    axes[0].set_xlim(0, 100)
    axes[0].set_ylim(0, 100)
    axes[0].set_xlabel('Actual Fare ($)')
    axes[0].set_ylabel('Predicted Fare ($)')
    axes[0].set_title('Actual vs Predicted Fare')
    axes[0].legend()
    
    # Residual distribution
    residuals = y_test_sample - y_pred_sample
    axes[1].hist(residuals, bins=50, edgecolor='black')
    axes[1].set_xlabel('Residual ($)')
    axes[1].set_ylabel('Frequency')
    axes[1].set_title('Residual Distribution')
    axes[1].axvline(x=0, color='r', linestyle='--')
    
    plt.tight_layout()
    plt.savefig(output_path / 'supervised_results.png', dpi=150)
    print(f"✓ Plot saved to {output_path / 'supervised_results.png'}")
    plt.close()


def main():
    parser = argparse.ArgumentParser(description='Train supervised learning model')
    parser.add_argument('--data-path', type=str, default='data_cleaned/yellow_tripdata_cleaned.parquet',
                        help='Path to cleaned data')
    parser.add_argument('--output-dir', type=str, default='outputs',
                        help='Output directory for results')
    parser.add_argument('--alpha', type=float, default=1.0,
                        help='Ridge regression alpha parameter')
    
    args = parser.parse_args()
    
    # Load and prepare data
    df = load_data(args.data_path)
    X_train, X_test, y_train, y_test, scaler, features = prepare_features(df)
    
    # Train models
    lr_model = train_linear_regression(X_train, y_train)
    ridge_model = train_ridge_regression(X_train, y_train, args.alpha)
    
    # Evaluate models
    lr_metrics, _ = evaluate_model(lr_model, X_test, y_test, 'Linear Regression')
    ridge_metrics, y_pred = evaluate_model(ridge_model, X_test, y_test, 'Ridge Regression')
    
    # Save results
    all_metrics = {
        'linear_regression': lr_metrics,
        'ridge_regression': ridge_metrics
    }
    save_results(all_metrics, args.output_dir)
    
    # Plot results
    plot_results(y_test, y_pred, args.output_dir)
    
    print("\n✓ Supervised learning pipeline completed successfully")


if __name__ == "__main__":
    main()