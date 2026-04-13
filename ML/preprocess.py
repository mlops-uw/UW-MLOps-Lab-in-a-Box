import pandas as pd
import argparse
from pathlib import Path
import glob
import os


def load_data(data_path: str) -> pd.DataFrame:
    """Load parquet data from a folder or a single parquet file."""
    print(f"Loading data from {data_path}")

    if os.path.isdir(data_path):
        parquet_files = glob.glob(os.path.join(data_path, "*.parquet"))
    else:
        parquet_files = [data_path] if data_path.endswith(".parquet") else []

    if not parquet_files:
        raise ValueError(f"No parquet files found in {data_path}")

    print(f"Found {len(parquet_files)} parquet file(s)")

    df = pd.concat(
        (pd.read_parquet(file) for file in parquet_files),
        ignore_index=True
    )

    print(f"Initial shape: {df.shape}")
    print("Initial columns:", df.columns.tolist())
    return df


def preprocess_data(df: pd.DataFrame) -> pd.DataFrame:
    """Clean and engineer features for downstream ML tasks."""

    columns_to_drop = [
        'store_and_fwd_flag', 'RatecodeID', 'congestion_surcharge',
        'Airport_fee', 'improvement_surcharge', 'mta_tax',
        'extra', 'tolls_amount', 'cbd_congestion_fee'
    ]

    existing_columns_to_drop = [col for col in columns_to_drop if col in df.columns]
    df = df.drop(columns=existing_columns_to_drop)

    print("Shape after dropping columns:", df.shape)

    required_cols = [
        'fare_amount', 'trip_distance', 'passenger_count',
        'total_amount', 'tpep_pickup_datetime', 'tpep_dropoff_datetime'
    ]
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns for preprocessing: {missing}")

    df['tpep_pickup_datetime'] = pd.to_datetime(df['tpep_pickup_datetime'])
    df['tpep_dropoff_datetime'] = pd.to_datetime(df['tpep_dropoff_datetime'])

    df = df[df['fare_amount'] > 0]
    df = df[df['trip_distance'] > 0]
    df = df[df['passenger_count'] > 0]
    df = df[df['fare_amount'] < 500]
    df = df[df['trip_distance'] < 100]
    df = df[df['passenger_count'] <= 6]
    df = df[df['total_amount'] > 0]

    print("Shape after filtering invalid rows/outliers:", df.shape)

    df['trip_duration_min'] = (
        df['tpep_dropoff_datetime'] - df['tpep_pickup_datetime']
    ).dt.total_seconds() / 60

    df = df[(df['trip_duration_min'] > 1) & (df['trip_duration_min'] < 180)]

    df['pickup_hour'] = df['tpep_pickup_datetime'].dt.hour
    df['pickup_dayofweek'] = df['tpep_pickup_datetime'].dt.dayofweek

    df = df.dropna()

    print("Shape after feature engineering:", df.shape)
    print("Final columns:", df.columns.tolist())
    print("\nNull counts:\n", df.isnull().sum())

    return df


def save_data(df: pd.DataFrame, output_dir: str):
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    output_file = output_path / "yellow_tripdata_preprocessed.parquet"
    df.to_parquet(output_file, index=False)

    print(f"Saved preprocessed data to {output_file}")


def main():
    parser = argparse.ArgumentParser(description="Preprocess NYC taxi data")
    parser.add_argument(
        "--data-path",
        type=str,
        required=True,
        help="Path to raw data folder or parquet file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs",
        help="Directory to save preprocessed data"
    )

    args = parser.parse_args()

    df = load_data(args.data_path)
    df_clean = preprocess_data(df)
    save_data(df_clean, args.output_dir)

    print("Preprocessing completed successfully")


if __name__ == "__main__":
    main()