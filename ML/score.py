# ---------------------------
# Model Scoring Endpoints
# NYC Taxi MLOps - Boeing x WIC x UW
# ---------------------------
# Serves two endpoints:
#   POST /predict-fare    — Linear Regression (fare prediction)
#   POST /predict-cluster — KMeans (zone cluster assignment)

import argparse
import json
import os
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

app = Flask(__name__)

# Global model and scaler references (loaded at startup)
lr_model = None
lr_scaler = None
kmeans_model = None
kmeans_scaler = None


def load_models(supervised_dir: str, unsupervised_dir: str):
    global lr_model, lr_scaler, kmeans_model, kmeans_scaler

    sup_path = Path(supervised_dir)
    unsup_path = Path(unsupervised_dir)

    # Load Linear Regression model and scaler
    lr_model = joblib.load(sup_path / "linear_regression" / "model.joblib")
    lr_scaler = joblib.load(sup_path / "feature_scaler" / "model.joblib")
    print(f"Loaded Linear Regression model from {sup_path}")

    # Load KMeans model
    kmeans_model = joblib.load(unsup_path / "kmeans" / "model.joblib")
    print(f"Loaded KMeans model from {unsup_path}")

    # Load KMeans scaler from unsupervised metrics to rebuild
    metrics = json.loads((unsup_path / "unsupervised_metrics.json").read_text())
    print(f"KMeans expects features: {metrics['features_used']}")


# ---------------------------
# POST /predict-fare
# Linear Regression: predict fare amount
# ---------------------------
# Input JSON:
# {
#   "trip_distance": 3.5,
#   "trip_duration_min": 15.0,
#   "pickup_hour": 14,
#   "passenger_count": 2
# }
@app.route("/predict-fare", methods=["POST"])
def predict_fare():
    try:
        data = request.get_json()

        required = ["trip_distance", "trip_duration_min", "pickup_hour", "passenger_count"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        features = pd.DataFrame([{
            "trip_distance": float(data["trip_distance"]),
            "trip_duration_min": float(data["trip_duration_min"]),
            "pickup_hour": int(data["pickup_hour"]),
            "passenger_count": int(data["passenger_count"]),
        }])

        features_scaled = lr_scaler.transform(features)
        prediction = lr_model.predict(features_scaled)[0]

        return jsonify({
            "predicted_fare_amount": round(float(prediction), 2),
            "model": "linear_regression",
            "input": data,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------
# POST /predict-cluster
# KMeans: assign zone cluster based on drop-off location aggregates
# ---------------------------
# Input JSON:
# {
#   "DOLocationID": 161,
#   "fare_amount": 12.50,
#   "trip_distance": 2.1,
#   "passenger_count": 1,
#   "pickup_hour": 9
# }
#
# In production, you would aggregate trip data by DOLocationID and then
# predict which cluster that zone belongs to. This endpoint accepts
# zone-level aggregate values directly for scoring.
@app.route("/predict-cluster", methods=["POST"])
def predict_cluster():
    try:
        data = request.get_json()

        required = ["DOLocationID", "fare_amount", "trip_distance", "passenger_count", "pickup_hour"]
        missing = [f for f in required if f not in data]
        if missing:
            return jsonify({"error": f"Missing fields: {missing}"}), 400

        # KMeans was trained on zone-level aggregated features:
        # [fare_amount, trip_distance, passenger_count, pickup_hour, trip_count]
        # trip_count is not available for a single request, default to 1
        features = np.array([[
            float(data["fare_amount"]),
            float(data["trip_distance"]),
            float(data["passenger_count"]),
            float(data["pickup_hour"]),
            float(data.get("trip_count", 1)),
        ]])

        cluster = int(kmeans_model.predict(features)[0])

        return jsonify({
            "DOLocationID": data["DOLocationID"],
            "predicted_cluster": cluster,
            "model": "kmeans",
            "input": data,
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ---------------------------
# GET /health
# ---------------------------
@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "models_loaded": {
            "linear_regression": lr_model is not None,
            "kmeans": kmeans_model is not None,
        }
    })


# ---------------------------
# Main
# ---------------------------
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Model Scoring Endpoints for NYC Taxi MLOps")
    parser.add_argument("--supervised-dir", type=str, required=True, help="Directory with supervised model artifacts")
    parser.add_argument("--unsupervised-dir", type=str, required=True, help="Directory with unsupervised model artifacts")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=5000, help="Port to bind")
    args = parser.parse_args()

    load_models(args.supervised_dir, args.unsupervised_dir)
    app.run(host=args.host, port=args.port)
