import argparse
import json
from pathlib import Path

import joblib
import mlflow
import mlflow.sklearn


def load_json(path: Path) -> dict:
    with path.open() as f:
        return json.load(f)


def load_model(model_path: Path):
    if not model_path.exists():
        raise FileNotFoundError(f"Expected model artifact at {model_path}")
    return joblib.load(model_path)


def register_supervised_models(models_dir: Path, linear_model_name: str, ridge_model_name: str):
    metrics = load_json(models_dir / "supervised_metrics.json")
    features = metrics["features_used"]

    model_specs = [
        ("linear_regression", "Linear Regression", linear_model_name),
        ("ridge_regression", "Ridge Regression", ridge_model_name),
    ]

    for artifact_name, display_name, registered_name in model_specs:
        model = load_model(models_dir / artifact_name / "model.joblib")
        model_metrics = metrics[artifact_name]

        with mlflow.start_run(run_name=f"register-{registered_name}"):
            mlflow.set_tags(
                {
                    "training_type": "supervised",
                    "model_family": display_name,
                    "target_column": "fare_amount",
                    "feature_columns": ",".join(features),
                }
            )
            mlflow.log_metrics(
                {
                    f"{artifact_name}_r2_score": model_metrics["r2_score"],
                    f"{artifact_name}_mae": model_metrics["mae"],
                    f"{artifact_name}_rmse": model_metrics["rmse"],
                }
            )
            mlflow.log_dict(model_metrics, f"{artifact_name}_metrics.json")
            mlflow.sklearn.log_model(
                sk_model=model,
                artifact_path=artifact_name,
                registered_model_name=registered_name,
            )

        print(f"Registered Azure ML model '{registered_name}'")


def register_unsupervised_model(models_dir: Path, model_name: str):
    metrics = load_json(models_dir / "unsupervised_metrics.json")
    model = load_model(models_dir / "kmeans" / "model.joblib")

    with mlflow.start_run(run_name=f"register-{model_name}"):
        mlflow.set_tags(
            {
                "training_type": "unsupervised",
                "model_family": metrics["model"],
                "feature_columns": ",".join(metrics["features_used"]),
            }
        )
        mlflow.log_params(
            {
                "n_clusters": metrics["n_clusters"],
                "sample_size_used": metrics["sample_size_used"],
            }
        )
        mlflow.log_metric("inertia", metrics["inertia"])
        mlflow.log_dict(metrics, "unsupervised_metrics.json")
        mlflow.sklearn.log_model(
            sk_model=model,
            artifact_path="kmeans",
            registered_model_name=model_name,
        )

    print(f"Registered Azure ML model '{model_name}'")


def main():
    parser = argparse.ArgumentParser(description="Register supervised and unsupervised models in Azure ML")
    parser.add_argument("--supervised-dir", required=True, help="Directory containing supervised model outputs")
    parser.add_argument("--unsupervised-dir", required=True, help="Directory containing unsupervised model outputs")
    parser.add_argument("--linear-model-name", default="taxi-fare-linear-regression")
    parser.add_argument("--ridge-model-name", default="taxi-fare-ridge-regression")
    parser.add_argument("--unsupervised-model-name", default="taxi-trip-kmeans")
    args = parser.parse_args()

    register_supervised_models(Path(args.supervised_dir), args.linear_model_name, args.ridge_model_name)
    register_unsupervised_model(Path(args.unsupervised_dir), args.unsupervised_model_name)
    print("Model registration completed successfully")


if __name__ == "__main__":
    main()
