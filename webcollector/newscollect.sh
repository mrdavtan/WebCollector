#!/bin/bash

# Function to handle the cleanup process
cleanup() {
    echo "Interrupt received. Cleaning up..."
    # Kill the background process if it's still running
    [[ -n $pid ]] && kill $pid
    # Any additional cleanup commands can go here
    echo "Cleanup complete. Exiting."
    exit 1  # Exit with a non-zero status to indicate interruption
}

# Set a trap to catch the SIGINT signal (Ctrl+C) and call the cleanup function
trap cleanup SIGINT

# Determine the directory of this script
script_dir=$(dirname "$(realpath "$0")")

# Assuming the virtual environment is located one directory up from the script directory
venv_dir=$(dirname "$script_dir")/.venv

# Activate the virtual environment
source "$venv_dir/bin/activate"

# Path to the config file, assuming it's in the same directory as this script
config_file="$script_dir/config.json"

# Use Python to extract values from the config file
articles_dir="$script_dir/$(python3 -c "import json; print(json.load(open('$config_file'))['articles_dir'])")"
sources_dir="$script_dir/$(python3 -c "import json; print(json.load(open('$config_file'))['sources_dir'])")"

# Construct the command to run collect.py
collect_cmd="python3 \"$script_dir/collect.py\" \"$sources_dir\""

# If a date argument was provided, append it to the collect.py command and print it
if [ "$#" -eq 1 ]; then
    collect_cmd="$collect_cmd \"$1\""
    echo "Provided date for collect.py: $1"
fi

# Debugging line to show the command being run
echo "Running collect.py with command: $collect_cmd"

# Run the collect.py script with or without the date argument
eval $collect_cmd &

pid=$!

# Wait for the first script to finish
wait $pid

echo "First script finished. Running the second script..."

# Run the second script
python3 "$script_dir/rem_dup.py" "$articles_dir"

echo "Second script finished. Running the third script..."

# Run the third script
python3 "$script_dir/archive.py" "$articles_dir"

echo "All scripts finished."

