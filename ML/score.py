# ---------------------------
# Model Scoring Script for Azure ML Managed Endpoints
# NYC Taxi MLOps - Boeing x WIC x UW
# ---------------------------
# Azure ML calls init() once at startup and run() per request.
# Serves both Linear Regression (fare prediction) and KMeans (zone clustering).

import json
import os
import numpy as np
import joblib


# Global model references
lr_model = None
lr_scaler = None
kmeans_model = None


def init():
    """Called once when the endpoint container starts."""
    global lr_model, lr_scaler, kmeans_model

    model_dir = os.environ["AZUREML_MODEL_DIR"]

    # Load Linear Regression model and scaler
    lr_model = joblib.load(os.path.join(model_dir, "linear_regression", "model.joblib"))
    lr_scaler = joblib.load(os.path.join(model_dir, "feature_scaler", "model.joblib"))

    # Load KMeans model
    kmeans_model = joblib.load(os.path.join(model_dir, "kmeans", "model.joblib"))

    print("All models loaded successfully.")


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

    features_scaled = lr_scaler.transform(features)
    prediction = lr_model.predict(features_scaled)[0]

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
