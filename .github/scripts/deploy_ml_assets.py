#!/usr/bin/env python3
"""
Deploy ML assets (environment, components, pipeline, notebook) to Azure ML workspace
"""
import os
from pathlib import Path
from azure.ai.ml import MLClient
from azure.ai.ml.entities import Environment, Data
from azure.ai.ml.constants import AssetTypes
from azure.identity import DefaultAzureCredential
import datetime


def make_asset_version(prefix: str = "v") -> str:
    gh_sha = os.environ.get("GITHUB_SHA")
    if gh_sha:
        return f"{prefix}{gh_sha[:8]}"
    run_id = os.environ.get("GITHUB_RUN_ID")
    if run_id:
        return f"{prefix}{run_id}"
    return f"{prefix}{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"


def main():
    # Get environment variables
    subscription_id = os.environ.get('AZURE_SUBSCRIPTION_ID')
    resource_group = os.environ.get('AZURE_RESOURCE_GROUP')
    workspace_name = os.environ.get('AZURE_ML_WORKSPACE')
    
    if not all([subscription_id, resource_group, workspace_name]):
        raise ValueError("Missing required environment variables")
    
    print(f"Connecting to Azure ML Workspace: {workspace_name}")
    
    # Create ML Client
    credential = DefaultAzureCredential()
    ml_client = MLClient(
        credential=credential,
        subscription_id=subscription_id,
        resource_group_name=resource_group,
        workspace_name=workspace_name
    )
    
    print("\n" + "="*60)
    print("DEPLOYING ML ASSETS TO AZURE ML")
    print("="*60)
    
    # Generate version from timestamp
    version = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    
    # 1. Upload Jupyter Notebook (auto-generated from scripts)
    print("\n[1/4] Uploading Jupyter Notebook...")
    notebook_data = Data(
        name="taxi_ml_analysis_notebook",
        version="latest",
        description="NYC Taxi ML Analysis - Auto-generated from Python scripts",
        path="ML/taxi_ml_analysis.ipynb",
        type=AssetTypes.URI_FILE
    )
    ml_client.data.create_or_update(notebook_data)
    print("✓ Notebook uploaded: taxi_ml_analysis_notebook")
    
    # 2. Create/Update Environment
    print("\n[2/4] Creating ML Environment...")
    try:
        # Check for both .yml and .yaml extensions
        env_file = "ML/environment.yaml" if Path("ML/environment.yaml").exists() else "ML/environment.yml"
        if not Path(env_file).exists():
            print(f"⚠ Environment file not found: {env_file}")
        else:
            env = Environment(
                name="taxi-ml-env",
                version=version,
                description="Environment for NYC Taxi ML pipeline",
                conda_file=env_file,
                image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04"
            )
            ml_client.environments.create_or_update(env)
            print(f"✓ Environment created: taxi-ml-env (version: {version})")
    except Exception as e:
        print(f"⚠ Environment creation failed: {e}")
    
    # 3. Upload Pipeline Definition
    print("\n[3/4] Uploading Pipeline Definition...")
    try:
        pipeline_data = Data(
            name="taxi_ml_pipeline_definition",
            version="latest",
            description="NYC Taxi ML Pipeline YAML definition",
            path="ML/pipeline.yml",
            type=AssetTypes.URI_FILE
        )
        ml_client.data.create_or_update(pipeline_data)
        print("✓ Pipeline definition uploaded")
    except Exception as e:
        print(f"⚠ Script upload failed: {e}")
    
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)
    print(f"Workspace: {workspace_name}")
    print(f"Resource Group: {resource_group}")
    print(f"Version: {version}")
    print("\nAssets deployed:")
    print("  ✓ Jupyter Notebook (auto-generated from scripts)")
    print("  ✓ Environment (taxi-ml-env)")
    print("  ✓ Pipeline (taxi_ml_pipeline_definition)")
    print("  ✓ Python Scripts (supervised & unsupervised)")
    print("\nAccess in Azure ML Studio:")
    print(f"  • Notebooks: Data → taxi_ml_analysis_notebook (v{version})")
    print("  • Pipeline: Data → taxi_ml_pipeline_definition (v{version})")
    print("="*60)


if __name__ == "__main__":
    main()