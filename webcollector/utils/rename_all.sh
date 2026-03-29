#!/bin/bash

# Directory where the directories to process are located
TARGET_DIR="./"

# Loop through each item in the target directory
for item in "$TARGET_DIR"/*; do
   # Check if the item is a directory
   if [ -d "$item" ]; then
       # Run the Python script with the directory as an argument
       python rename_script.py "$item"
   fi
done

