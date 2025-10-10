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
STRATEGY_CLASS_NAME=""

# Parse input arguments
for arg in "$@"; do
    case $arg in
        --strategy_class_name=*) STRATEGY_CLASS_NAME="${arg#*=}" ;;
        *) echo "Unknown argument: $arg"; exit 1 ;;
    esac
done

# Check if required parameters are provided
if [[ -z "$STRATEGY_CLASS_NAME" ]]; then
    echo "Error: --strategy_class_name must be provided."
    echo "Available strategies: TibetanMastiffTWStrategy, PeterWuStrategy, AlanTwStrategy1, AlanTwStrategy2, AlanTWStrategyC, AlanTWStrategyE, RAndDManagementStrategy"
    exit 1
fi

# Display the strategy being executed
echo "Executing backtest for strategy: $STRATEGY_CLASS_NAME"
echo "Timestamp: $(date)"

# Run the Python script
echo "Running Python script 'backtest_executor.py'..."
python -m jobs.backtest_executor --strategy_class_name "$STRATEGY_CLASS_NAME"

# Deactivate conda environment
echo "Deactivating conda environment..."
conda deactivate

echo "Script execution completed."