#!/bin/bash

echo "Activating miniconda environment 'stock-analysis'..."
source /opt/miniconda3/etc/profile.d/conda.sh
conda activate stock-analysis

# Change to project root directory
cd /home/mirlab/stock-analysis
# Set PYTHONPATH to the current directory
export PYTHONPATH=$(pwd)

# Get the current time (in 24-hour format, in HHMM)
current_time=$(date +"%H%M")
echo "Current time: $current_time"

# Set the extra_bid_pct parameter, set different parameters according to different times
if [ "$current_time" -eq "0930" ]; then
    EXTRA_BID_PCT=0
elif [ "$current_time" -eq "1300" ]; then
    EXTRA_BID_PCT=0.01
else
    EXTRA_BID_PCT=0
fi
echo "Extra bid percentage: $EXTRA_BID_PCT"

USER_NAME="junting"
BROKER_NAME="fugle"

# If view-only mode is required, add the --view_only parameter; otherwise, leave it blank.
VIEW_ONLY_FLAG="--view_only"

# Execute order_executor.py
echo "Running Python script 'order_executor.py'..."
python jobs/order_executor.py --user_name $USER_NAME --broker_name $BROKER_NAME --extra_bid_pct $EXTRA_BID_PCT $VIEW_ONLY_FLAG

# Exit anaconda environment
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."
