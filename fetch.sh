#!/bin/bash

# Default values
USER_NAME=""
BROKER_NAME=""

# Parse input arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --user_name=*) USER_NAME="${1#*=}"; shift ;;
        --broker_name=*) BROKER_NAME="${1#*=}"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
done

# Check if required parameters are provided
if [[ -z "$USER_NAME" || -z "$BROKER_NAME" ]]; then
    echo "Error: Missing required arguments --user_name and --broker_name"
    exit 1
fi

# Activate conda env
echo "Activating miniconda environment 'stock-analysis'..."
source /home/junting/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# Change to project root directory
cd /home/junting/stock-analysis
export PYTHONPATH=$(pwd)
# The version of libstdc++.so.6 on the system is too old
export LD_PRELOAD=$CONDA_PREFIX/lib/libstdc++.so.6

# Run the Python script
echo "Running Python script 'scheduler.py'..."
python -m jobs.scheduler --user_name "$USER_NAME" --broker_name "$BROKER_NAME"

# Deactivate conda environment
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."
