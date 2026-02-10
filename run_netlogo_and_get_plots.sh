#!/bin/bash

# parse arguments
MODE=""
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --mode) MODE="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

# Define variables based on mode
# We define the specific file, experiment name, and file indicator for each mode.
if [ "$MODE" == "surround" ]; then
    MODEL_FILE="project_sheep_surround_logic.nlogox"
    EXPERIMENT="find-best-dog-number-surround" 
    INDICATOR=""

elif [ "$MODE" == "hybrid" ]; then
    MODEL_FILE="project_sheep_surround_strombom_hybrid.nlogox"
    EXPERIMENT="find-best-dog-number-hybrid"
    INDICATOR="-hybrid"

elif [ "$MODE" == "rotate" ]; then
    MODEL_FILE="project_sheep_surround_strombom_hybrid_rotate.nlogox"
    EXPERIMENT="find-best-dog-number-rotate"
    INDICATOR="-rotate"

else
    echo "Error: You must specify a valid mode: --mode [hybrid | rotate | surround]"
    exit 1
fi

TIME_INDICATOR=$(date "+%d_%H%M")

CSV_FILENAME="results_100_sheep_N_dogs_and_speeds${INDICATOR}_${TIME_INDICATOR}.csv"
PLOT_FILENAME="plots${INDICATOR}_${TIME_INDICATOR}.png"

echo "=========================================================="
echo "STARTING AUTOMATED RUN"
echo "----------------------------------------------------------"
echo "Model:      $MODEL_FILE"
echo "Experiment: $EXPERIMENT"
echo "CSV Output: $CSV_FILENAME"
echo "Plot Output: $PLOT_FILENAME"
echo "=========================================================="

# Run NetLogo headless (behavior space experiment)
./NetLogo_Console \
    --headless \
    --model "$MODEL_FILE" \
    --experiment "$EXPERIMENT" \
    --table "$CSV_FILENAME"

# Check if NetLogo run was successful
if [ $? -eq 0 ]; then
    echo "NetLogo simulation complete. Starting analysis..."
    
    # Run python analysis
    python3 data_analysis.py "$CSV_FILENAME" "$PLOT_FILENAME"
    
    if [ $? -eq 0 ]; then
        echo "Analysis complete. Plot saved to: $PLOT_FILENAME"
    else
        echo "Error during python analysis."
    fi
else
    echo "Error during NetLogo simulation."
fi
