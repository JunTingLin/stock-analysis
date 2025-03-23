#!/bin/bash

# Activate the miniconda environment "stock-analysis"
echo "Activating miniconda environment 'stock-analysis'..."
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# Change to project root directory
cd /home/mirlab/stock-analysis

# Set default user name and broker name
USER_NAME="junting"
BROKER_NAME="fugle"

# Run the scheduler Python script
echo "Running Python script 'scheduler.py'..."
python -m jobs.scheduler --user_name "$USER_NAME" --broker_name "$BROKER_NAME"

# Deactivate the conda environment
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."
