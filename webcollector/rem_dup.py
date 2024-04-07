#!/bin/env python3

import os
import glob
import re
import sys

def count_json_files(directory):
    # Use glob to count .json files in the directory
    return len(glob.glob(os.path.join(directory, '*.json')))

def sanitize_filename(filename):
    # Remove problematic characters and ensure the filename ends with ".json"
    sanitized = re.sub(r"[^a-zA-Z0-9._-]", "", filename)
    if not sanitized.endswith(".json"):
        sanitized = re.sub(r"\.json.*$", ".json", sanitized, flags=re.IGNORECASE)
    return sanitized

def remove_smaller_file_if_duplicate(directory):
    file_tracker = {}
    removed_files = []

    for file_path in glob.glob(os.path.join(directory, '*.json')):
        filename = os.path.basename(file_path)
        sanitized_filename = sanitize_filename(filename)
        sanitized_file_path = os.path.join(directory, sanitized_filename)

        # Only rename if the sanitized filename is different
        if sanitized_file_path != file_path:
            os.rename(file_path, sanitized_file_path)

        prefix = sanitized_filename[:20]
        file_size = os.path.getsize(sanitized_file_path)

        if prefix in file_tracker:
            existing_file_path, existing_file_size = file_tracker[prefix]
            if file_size > existing_file_size:
                os.remove(existing_file_path)
                removed_files.append(existing_file_path)
                file_tracker[prefix] = (sanitized_file_path, file_size)
            else:
                os.remove(sanitized_file_path)
                removed_files.append(sanitized_file_path)
        else:
            file_tracker[prefix] = (sanitized_file_path, file_size)

    return removed_files

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python remove_duplicate.py <directory_path>")
        sys.exit(1)

    directory_path = sys.argv[1]

    # Check if the provided directory path exists
    if not os.path.isdir(directory_path):
        print(f"Error: {directory_path} is not a valid directory.")
        sys.exit(1)

    # Count the .json files before removal
    count_before = count_json_files(directory_path)

    # Remove smaller files if duplicates exist and get the list of removed files
    removed_files = remove_smaller_file_if_duplicate(directory_path)

    # Count the .json files after removal
    count_after = count_json_files(directory_path)

    # Print the counts and the number of files removed
    print(f"Number of .json files before: {count_before}")
    print(f"Number of .json files removed: {len(removed_files)}")
    print(f"Number of .json files after: {count_after}")
