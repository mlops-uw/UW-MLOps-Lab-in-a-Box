# ---------------------------
# Model Scoring Script for KMeans Cluster Endpoint
# NYC Taxi MLOps - Boeing x WIC x UW
# ---------------------------

import json
import os
import glob
import numpy as np
import joblib
import pickle


kmeans_model = None


def find_model_file(base_dir, subdir, extensions=("model.pkl", "model.joblib")):
    for ext in extensions:
        direct = os.path.join(base_dir, subdir, ext)
        if os.path.exists(direct):
            return direct
        pattern = os.path.join(base_dir, "**", subdir, ext)
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    # Fallback: search for any model file at root
    for ext in extensions:
        pattern = os.path.join(base_dir, "**", ext)
        matches = glob.glob(pattern, recursive=True)
        if matches:
            return matches[0]
    raise FileNotFoundError(f"No model file found in {base_dir}")


def load_model(path):
    if path.endswith(".pkl"):
        with open(path, "rb") as f:
            return pickle.load(f)
    return joblib.load(path)


def init():
    global kmeans_model
    model_dir = os.environ["AZUREML_MODEL_DIR"]
    print(f"Model directory: {model_dir}")

    for root, dirs, files in os.walk(model_dir):
        level = root.replace(model_dir, "").count(os.sep)
        indent = " " * 2 * level
        print(f"{indent}{os.path.basename(root)}/")
        for file in files:
            print(f"{indent}  {file}")

    kmeans_path = find_model_file(model_dir, "kmeans")
    kmeans_model = load_model(kmeans_path)
    print(f"Loaded KMeans from {kmeans_path}")


def run(raw_data):
    try:
        data = json.loads(raw_data)

        required = ["DOLocationID", "fare_amount", "trip_distance", "passenger_count", "pickup_hour"]
        missing = [f for f in required if f not in data]
        if missing:
            return json.dumps({"error": f"Missing fields: {missing}"})

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

    except Exception as e:
        return json.dumps({"error": str(e)})