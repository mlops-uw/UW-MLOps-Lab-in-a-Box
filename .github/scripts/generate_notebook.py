#!/usr/bin/env python3
"""
Generate Jupyter notebook from Python scripts and deploy to Azure ML
"""
import json
import re
from pathlib import Path


def python_to_notebook_cells(python_file: str, title: str) -> list:
    """Convert Python script to notebook cells"""
    cells = []
    
    # Add title cell
    cells.append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [f"# {title}\n"]
    })
    
    with open(python_file, 'r') as f:
        content = f.read()
    
    # Remove if __name__ == "__main__" block
    content = re.sub(r'if __name__ == "__main__":.*', '', content, flags=re.DOTALL)
    
    # Split by function definitions and docstrings
    lines = content.split('\n')
    current_cell = []
    in_docstring = False
    docstring_content = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check for docstring start
        if '"""' in line or "'''" in line:
            if in_docstring:
                # End of docstring - create markdown cell
                docstring_content.append(line.strip('"""').strip("'''").strip())
                if docstring_content:
                    cells.append({
                        "cell_type": "markdown",
                        "metadata": {},
                        "source": ['\n'.join(docstring_content) + '\n']
                    })
                docstring_content = []
                in_docstring = False
            else:
                # Start of docstring
                if current_cell:
                    cells.append({
                        "cell_type": "code",
                        "execution_count": None,
                        "metadata": {},
                        "outputs": [],
                        "source": ['\n'.join(current_cell) + '\n']
                    })
                    current_cell = []
                in_docstring = True
                docstring_content.append(line.strip('"""').strip("'''").strip())
            i += 1
            continue
        
        if in_docstring:
            docstring_content.append(line.strip())
            i += 1
            continue
        
        # Check for function definition - create new cell
        if line.startswith('def ') or line.startswith('class '):
            if current_cell:
                cells.append({
                    "cell_type": "code",
                    "execution_count": None,
                    "metadata": {},
                    "outputs": [],
                    "source": ['\n'.join(current_cell) + '\n']
                })
                current_cell = []
            
            # Add markdown for function/class name
            func_name = line.split('(')[0].replace('def ', '').replace('class ', '').strip()
            cells.append({
                "cell_type": "markdown",
                "metadata": {},
                "source": [f"## {func_name}\n"]
            })
        
        # Skip imports at the top, argparse, and main function
        if not (line.startswith('import ') or line.startswith('from ') or 
                'argparse' in line or 'parser' in line or line.strip().startswith('#')):
            if line.strip():  # Skip empty lines at boundaries
                current_cell.append(line)
        elif line.startswith('import ') or line.startswith('from '):
            # Keep imports in first cell
            if not current_cell or i < 20:  # First 20 lines likely imports
                current_cell.append(line)
        
        i += 1
    
    # Add remaining cell
    if current_cell:
        cells.append({
            "cell_type": "code",
            "execution_count": None,
            "metadata": {},
            "outputs": [],
            "source": ['\n'.join(current_cell) + '\n']
        })
    
    return cells


def create_notebook_from_scripts():
    """Create a Jupyter notebook from Python scripts"""
    
    # Read the Python scripts
    supervised_file = "ML/supervised_learning.py"
    unsupervised_file = "ML/unsupervised_learning.py"
    
    notebook = {
        "cells": [],
        "metadata": {
            "kernelspec": {
                "display_name": "Python 3",
                "language": "python",
                "name": "python3"
            },
            "language_info": {
                "codemirror_mode": {
                    "name": "ipython",
                    "version": 3
                },
                "file_extension": ".py",
                "mimetype": "text/x-python",
                "name": "python",
                "nbconvert_exporter": "python",
                "pygments_lexer": "ipython3",
                "version": "3.9.0"
            }
        },
        "nbformat": 4,
        "nbformat_minor": 4
    }
    
    # Add main title
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": [
            "# NYC Taxi ML Analysis\n",
            "## Supervised and Unsupervised Learning\n",
            "\n",
            "This notebook contains machine learning analysis for NYC taxi data.\n",
            "- Part 1: Supervised Learning (Fare Prediction)\n",
            "- Part 2: Unsupervised Learning (Trip Clustering)\n"
        ]
    })
    
    # Add imports cell
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["---\n# Part 1: Supervised Learning - Fare Prediction\n---\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "import pandas as pd\n",
            "import numpy as np\n",
            "import matplotlib.pyplot as plt\n",
            "import seaborn as sns\n",
            "from sklearn.linear_model import LinearRegression, Ridge\n",
            "from sklearn.model_selection import train_test_split\n",
            "from sklearn.preprocessing import StandardScaler\n",
            "from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score\n",
            "from pathlib import Path\n",
            "\n",
            "sns.set_style('whitegrid')\n"
        ]
    })
    
    # Add supervised learning code
    with open(supervised_file, 'r') as f:
        supervised_code = f.read()
    
    # Extract main execution flow for supervised
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Load and Prepare Data\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Load cleaned data\n",
            "df = pd.read_parquet('data_cleaned/yellow_tripdata_cleaned.parquet')\n",
            "print(f'Shape: {df.shape}')\n",
            "df.head()\n"
        ]
    })
    
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Feature Engineering and Train-Test Split\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "features = ['trip_distance', 'trip_duration_min', 'pickup_hour', 'passenger_count']\n",
            "target = 'fare_amount'\n",
            "\n",
            "X = df[features]\n",
            "y = df[target]\n",
            "\n",
            "# Train-test split\n",
            "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)\n",
            "\n",
            "# Normalize features\n",
            "scaler = StandardScaler()\n",
            "X_train_scaled = scaler.fit_transform(X_train)\n",
            "X_test_scaled = scaler.transform(X_test)\n",
            "\n",
            "print(f'Training set: {X_train.shape[0]:,} rows')\n",
            "print(f'Test set: {X_test.shape[0]:,} rows')\n"
        ]
    })
    
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Train Linear Regression (No Regularization)\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Train Linear Regression\n",
            "model = LinearRegression()\n",
            "model.fit(X_train_scaled, y_train)\n",
            "y_pred = model.predict(X_test_scaled)\n",
            "\n",
            "print('=== Linear Regression Results ===')\n",
            "print(f'R² Score: {r2_score(y_test, y_pred):.4f}')\n",
            "print(f'MAE: ${mean_absolute_error(y_test, y_pred):.2f}')\n",
            "print(f'RMSE: ${np.sqrt(mean_squared_error(y_test, y_pred)):.2f}')\n"
        ]
    })
    
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Train Ridge Regression (With Regularization)\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Train Ridge Regression\n",
            "ridge_model = Ridge(alpha=1.0, random_state=42)\n",
            "ridge_model.fit(X_train_scaled, y_train)\n",
            "y_pred_ridge = ridge_model.predict(X_test_scaled)\n",
            "\n",
            "print('=== Ridge Regression Results ===')\n",
            "print(f'R² Score: {r2_score(y_test, y_pred_ridge):.4f}')\n",
            "print(f'MAE: ${mean_absolute_error(y_test, y_pred_ridge):.2f}')\n",
            "print(f'RMSE: ${np.sqrt(mean_squared_error(y_test, y_pred_ridge)):.2f}')\n"
        ]
    })
    
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Visualize Results\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Sample for visualization\n",
            "sample_idx = X_test.sample(n=5000, random_state=42).index\n",
            "y_test_sample = y_test.loc[sample_idx]\n",
            "y_pred_sample = pd.Series(y_pred_ridge, index=y_test.index).loc[sample_idx]\n",
            "\n",
            "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
            "\n",
            "# Actual vs Predicted\n",
            "axes[0].scatter(y_test_sample, y_pred_sample, alpha=0.3, s=5)\n",
            "axes[0].plot([0, 100], [0, 100], 'r--', label='Perfect prediction')\n",
            "axes[0].set_xlim(0, 100)\n",
            "axes[0].set_ylim(0, 100)\n",
            "axes[0].set_xlabel('Actual Fare ($)')\n",
            "axes[0].set_ylabel('Predicted Fare ($)')\n",
            "axes[0].set_title('Actual vs Predicted Fare')\n",
            "axes[0].legend()\n",
            "\n",
            "# Residuals\n",
            "residuals = y_test_sample - y_pred_sample\n",
            "axes[1].hist(residuals, bins=50, edgecolor='black')\n",
            "axes[1].set_xlabel('Residual ($)')\n",
            "axes[1].set_ylabel('Frequency')\n",
            "axes[1].set_title('Residual Distribution')\n",
            "axes[1].axvline(x=0, color='r', linestyle='--')\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.show()\n"
        ]
    })
    
    # Add unsupervised learning section
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["---\n# Part 2: Unsupervised Learning - K-Means Clustering\n---\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "from sklearn.cluster import MiniBatchKMeans\n",
            "from sklearn.preprocessing import StandardScaler\n"
        ]
    })
    
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Prepare Features for Clustering\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Select features and sample\n",
            "cluster_features = ['PULocationID', 'pickup_hour', 'trip_distance', 'fare_amount']\n",
            "df_sample = df[cluster_features].sample(n=100000, random_state=42)\n",
            "\n",
            "# Normalize\n",
            "scaler = StandardScaler()\n",
            "X_scaled = scaler.fit_transform(df_sample)\n",
            "\n",
            "print(f'Sample shape: {df_sample.shape}')\n",
            "print(f'Mean: {X_scaled.mean(axis=0).round(4)}')\n",
            "print(f'Std: {X_scaled.std(axis=0).round(4)}')\n"
        ]
    })
    
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Elbow Method - Find Optimal K\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Elbow method\n",
            "inertias = []\n",
            "K_range = range(2, 11)\n",
            "\n",
            "for k in K_range:\n",
            "    kmeans = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=10000)\n",
            "    kmeans.fit(X_scaled)\n",
            "    inertias.append(kmeans.inertia_)\n",
            "    print(f'K={k}, Inertia={kmeans.inertia_:.0f}')\n",
            "\n",
            "# Plot elbow\n",
            "fig, ax = plt.subplots(figsize=(10, 5))\n",
            "ax.plot(K_range, inertias, marker='o', color='steelblue')\n",
            "ax.set_title('Elbow Method - Optimal Number of Clusters')\n",
            "ax.set_xlabel('Number of Clusters (K)')\n",
            "ax.set_ylabel('Inertia')\n",
            "plt.tight_layout()\n",
            "plt.show()\n"
        ]
    })
    
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Train K-Means with K=4\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "# Fit K-Means\n",
            "kmeans = MiniBatchKMeans(n_clusters=4, random_state=42, batch_size=10000)\n",
            "df_sample['cluster'] = kmeans.fit_predict(X_scaled)\n",
            "\n",
            "# Analyze clusters\n",
            "print('=== Cluster Summary ===')\n",
            "print(df_sample.groupby('cluster')[cluster_features].mean().round(2))\n",
            "print('\\n=== Cluster Sizes ===')\n",
            "print(df_sample['cluster'].value_counts().sort_index())\n"
        ]
    })
    
    notebook["cells"].append({
        "cell_type": "markdown",
        "metadata": {},
        "source": ["## Visualize Clusters\n"]
    })
    
    notebook["cells"].append({
        "cell_type": "code",
        "execution_count": None,
        "metadata": {},
        "outputs": [],
        "source": [
            "fig, axes = plt.subplots(1, 2, figsize=(14, 5))\n",
            "colors = ['#2196F3', '#FF9800', '#4CAF50', '#E91E63']\n",
            "\n",
            "# Scatter plot\n",
            "for c in range(4):\n",
            "    mask = df_sample['cluster'] == c\n",
            "    axes[0].scatter(df_sample.loc[mask, 'pickup_hour'],\n",
            "                    df_sample.loc[mask, 'fare_amount'],\n",
            "                    alpha=0.3, s=5, c=colors[c], label=f'Cluster {c}')\n",
            "axes[0].set_xlabel('Pickup Hour')\n",
            "axes[0].set_ylabel('Fare Amount ($)')\n",
            "axes[0].set_title('Clusters: Pickup Hour vs Fare')\n",
            "axes[0].legend()\n",
            "\n",
            "# Bar chart\n",
            "cluster_stats = df_sample.groupby('cluster')['fare_amount'].mean()\n",
            "cluster_stats.plot(kind='bar', ax=axes[1], color=colors)\n",
            "axes[1].set_title('Average Fare by Cluster')\n",
            "axes[1].set_xlabel('Cluster')\n",
            "axes[1].set_ylabel('Average Fare ($)')\n",
            "axes[1].set_xticklabels([f'C{i}' for i in range(4)], rotation=0)\n",
            "\n",
            "plt.tight_layout()\n",
            "plt.show()\n"
        ]
    })
    
    # Save notebook
    output_path = Path("ML/taxi_ml_analysis.ipynb")
    with open(output_path, 'w') as f:
        json.dump(notebook, f, indent=2)
    
    print(f"✓ Notebook generated: {output_path}")
    return str(output_path)


if __name__ == "__main__":
    create_notebook_from_scripts()