# ---------------------------
# Model Scoring Script for Azure ML Managed Endpoints
# NYC Taxi MLOps - Boeing x WIC x UW
# ---------------------------
# Azure ML calls init() once at startup and run() per request.
# Serves both Linear Regression (fare prediction) and KMeans (zone clustering).

import json
import os
import glob
import numpy as np
import joblib
import pickle


# Global model references
lr_model = None
lr_scaler = None
kmeans_model = None


def find_model_file(base_dir, subdir, extensions=("model.pkl", "model.joblib")):
    """Find a model file within the Azure ML model directory structure."""
    # Azure ML mounts models at AZUREML_MODEL_DIR/<version>/<artifact_path>/
    # Try direct path first, then search recursively
    for ext in extensions:
        # Direct path
        direct = os.path.join(base_dir, subdir, ext)
        if os.path.exists(direct):
            return direct
        # Search recursively (handles versioned subdirs like 3/linear_regression/)
        pattern = os.path.join(base_dir, "**", subdir, ext)
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    raise FileNotFoundError(f"No model file found for '{subdir}' in {base_dir}")


def load_model(path):
    """Load a model from either .pkl or .joblib file."""
    if path.endswith(".pkl"):
        with open(path, "rb") as f:
            return pickle.load(f)
    return joblib.load(path)


def init():
    """Called once when the endpoint container starts."""
    global lr_model, lr_scaler, kmeans_model

    model_dir = os.environ["AZUREML_MODEL_DIR"]
    print(f"Model directory: {model_dir}")

    # List directory contents for debugging
    for root, dirs, files in os.walk(model_dir):
        level = root.replace(model_dir, "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        subindent = " " * 2 * (level + 1)
        for file in files:
            print(f"{subindent}{file}")

    # Load Linear Regression model
    lr_path = find_model_file(model_dir, "linear_regression")
    lr_model = load_model(lr_path)
    print(f"Loaded Linear Regression from {lr_path}")

    # Load scaler if available, otherwise skip scaling
    try:
        scaler_path = find_model_file(model_dir, "feature_scaler")
        lr_scaler = load_model(scaler_path)
        print(f"Loaded scaler from {scaler_path}")
    except FileNotFoundError:
        lr_scaler = None
        print("No scaler found, will use raw features")

    # Load KMeans model - this is from a different registered model
    # If deployed separately, it will be in its own AZUREML_MODEL_DIR
    # If co-located, search for it
    try:
        kmeans_path = find_model_file(model_dir, "kmeans")
        kmeans_model = load_model(kmeans_path)
        print(f"Loaded KMeans from {kmeans_path}")
    except FileNotFoundError:
        kmeans_model = None
        print("KMeans model not found in this deployment. Cluster endpoint unavailable.")

    print("Model loading complete.")


def run(raw_data):
    """Called per request. Routes to the appropriate model based on 'model' field."""
    try:
        data = json.loads(raw_data)
        model_type = data.get("model", "linear_regression")

        if model_type == "linear_regression":
            return predict_fare(data)
        elif model_type == "kmeans":
            return predict_cluster(data)
        else:
            return json.dumps({"error": f"Unknown model type: {model_type}. Use 'linear_regression' or 'kmeans'."})

    except Exception as e:
        return json.dumps({"error": str(e)})


def predict_fare(data):
    """
    Linear Regression: predict fare amount.
    Input:
    {
        "model": "linear_regression",
        "trip_distance": 3.5,
        "trip_duration_min": 15.0,
        "pickup_hour": 14,
        "passenger_count": 2
    }
    """
    required = ["trip_distance", "trip_duration_min", "pickup_hour", "passenger_count"]
    missing = [f for f in required if f not in data]
    if missing:
        return json.dumps({"error": f"Missing fields: {missing}"})

    features = np.array([[
        float(data["trip_distance"]),
        float(data["trip_duration_min"]),
        float(data["pickup_hour"]),
        int(data["passenger_count"]),
    ]])

    if lr_scaler is not None:
        features = lr_scaler.transform(features)

    prediction = lr_model.predict(features)[0]

    return json.dumps({
        "predicted_fare_amount": round(float(prediction), 2),
        "model": "linear_regression",
    })


def predict_cluster(data):
    """
    KMeans: assign zone cluster based on drop-off location aggregates.
    Input:
    {
        "model": "kmeans",
        "DOLocationID": 161,
        "fare_amount": 12.50,
        "trip_distance": 2.1,
        "passenger_count": 1,
        "pickup_hour": 9
    }
    """
    if kmeans_model is None:
        return json.dumps({"error": "KMeans model not loaded in this deployment"})

    required = ["DOLocationID", "fare_amount", "trip_distance", "passenger_count", "pickup_hour"]
    missing = [f for f in required if f not in data]
    if missing:
        return json.dumps({"error": f"Missing fields: {missing}"})

    # KMeans trained on: [fare_amount, trip_distance, passenger_count, pickup_hour, trip_count]
    features = np.array([[
        float(data["fare_amount"]),
        float(data["trip_distance"]),
        float(data["passenger_count"]),
        float(data["pickup_hour"]),
        float(data.get("trip_count", 1)),
    ]])

    cluster = int(kmeans_model.predict(features)[0])

    return json.dumps({
        "DOLocationID": data["DOLocationID"],
        "predicted_cluster": cluster,
        "model": "kmeans",
    })
