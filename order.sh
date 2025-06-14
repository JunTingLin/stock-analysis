#!/bin/bash

echo "Activating miniconda environment 'stock-analysis'..."
source /home/junting/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# Change to project root directory
cd /home/junting/stock-analysis
# Set PYTHONPATH to the current directory
export PYTHONPATH=$(pwd)
# The version of libstdc++.so.6 on the system is too old
export LD_PRELOAD=$CONDA_PREFIX/lib/libstdc++.so.6

# Default values
USER_NAME=""
BROKER_NAME=""
EXTRA_BID_PCT=0  # Default value
VIEW_ONLY_FLAG=""

# Parse input arguments
for arg in "$@"; do
    case $arg in
        --user_name=*) USER_NAME="${arg#*=}" ;;
        --broker_name=*) BROKER_NAME="${arg#*=}" ;;
        --extra_bid_pct=*) EXTRA_BID_PCT="${arg#*=}" ;;
        --view_only) VIEW_ONLY_FLAG="--view_only" ;;
        *) echo "Unknown argument: $arg"; exit 1 ;;
    esac
done

# Check if required parameters are provided
if [[ -z "$USER_NAME" || -z "$BROKER_NAME" ]]; then
    echo "Error: --user_name and --broker_name must be provided."
    exit 1
fi

# Get current time in HHMM format (for logging purposes)
current_time=$(date +"%H%M")
echo "Current time: $current_time"

echo "Extra bid percentage: $EXTRA_BID_PCT"

# Run the Python script
echo "Running Python script 'order_executor.py'..."
python jobs/order_executor.py --user_name "$USER_NAME" --broker_name "$BROKER_NAME" --extra_bid_pct "$EXTRA_BID_PCT" $VIEW_ONLY_FLAG

# Deactivate conda environment
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."