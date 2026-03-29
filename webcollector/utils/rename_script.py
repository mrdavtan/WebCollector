#!/bin/env python3

import os
import sys
import re

def rename_files(source_directory):
    # Define a regex pattern to match filenames with the format source_title_YYYYMMDD_HHMM.json
    pattern = re.compile(r'(.*)_(\d{8})_(\d{4})\.json$')

    for filename in os.listdir(source_directory):
        match = pattern.match(filename)
        if match:
            # Extract components from the filename
            prefix = match.group(1)
            date = match.group(2)
            # Construct the new filename by omitting the time component
            new_filename = f"{prefix}_{date}.json"
            old_file_path = os.path.join(source_directory, filename)
            new_file_path = os.path.join(source_directory, new_filename)

            # Rename the file
            os.rename(old_file_path, new_file_path)
            print(f"Renamed {filename} to {new_filename}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python rename_script.py <directory_path>")
        sys.exit(1)

    source_directory = sys.argv[1]

    # Check if the provided source directory exists and is a directory
    if not os.path.isdir(source_directory):
        print(f"Error: {source_directory} is not a valid directory.")
        sys.exit(1)

    rename_files(source_directory)

