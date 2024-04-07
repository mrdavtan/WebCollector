#!/bin/bash

# Load the config file
config_file="config.json"
script_dir=$(jq -r '.script_dir' "$config_file")
articles_dir=$(jq -r '.articles_dir' "$config_file")
sources_dir=$(jq -r '.sources_dir' "$config_file")

# Activate the virtual environment
source /home/davtan/code/retrievers/newscollector/.venv/bin/activate

# Run the first script
python3 "$script_dir/collect.py" "$script_dir/$sources_dir" &

pid=$!

# Wait for the first script to finish
wait $pid

echo "First script finished. Running the second script..."

# Run the second script
python3 "$script_dir/rem_dup.py" "$script_dir/$articles_dir"

echo "Second script finished. Running the third script..."

# Run the third script
python3 "$script_dir/archive.py" "$script_dir/$articles_dir"

echo "All scripts finished."
