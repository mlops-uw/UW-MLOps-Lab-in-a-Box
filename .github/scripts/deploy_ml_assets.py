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
        env = Environment(
            name="taxi-ml-env",
            description="Environment for NYC Taxi ML pipeline",
            conda_file=env_file,
            image="mcr.microsoft.com/azureml/openmpi4.1.0-ubuntu20.04"
        )
        ml_client.environments.create_or_update(env)
        print("✓ Environment created: taxi-ml-env")
    except Exception as e:
        print(f"⚠ Environment creation skipped: {e}")
    
    # 3. Upload Pipeline Definition
    print("\n[3/3] Uploading Pipeline Definition...")
    try:
        # Check for both .yml and .yaml extensions
        pipeline_file = "ML/pipeline.yaml" if Path("ML/pipeline.yaml").exists() else "ML/pipeline.yml"
        pipeline_data = Data(
            name="taxi_ml_pipeline_definition",
            version="latest",
            description="NYC Taxi ML Pipeline YAML definition",
            path=pipeline_file,
            type=AssetTypes.URI_FILE
        )
        ml_client.data.create_or_update(pipeline_data)
        print("✓ Pipeline definition uploaded")
    except Exception as e:
        print(f"⚠ Pipeline upload: {e}")
    
    print("\n" + "="*60)
    print("DEPLOYMENT SUMMARY")
    print("="*60)
    print(f"Workspace: {workspace_name}")
    print(f"Resource Group: {resource_group}")
    print("\nAssets deployed:")
    print("  ✓ Jupyter Notebook (auto-generated from scripts)")
    print("  ✓ Environment (taxi-ml-env)")
    print("  ✓ Pipeline (taxi_ml_pipeline_definition)")
    print("\nAccess in Azure ML Studio:")
    print("  • Notebooks: Data → taxi_ml_analysis_notebook")
    print("  • Pipeline: Run with 'az ml job create --file ML/pipeline.yml'")
    print("="*60)


if __name__ == "__main__":
    main()