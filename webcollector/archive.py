#!/bin/env python3

import os
import shutil
from datetime import datetime
import sys

def archive_files(source_directory):
    directories_created = set()
    files_moved = {}

    # Iterate over the files in the source directory
    for filename in os.listdir(source_directory):
        if filename.endswith(".json"):
            file_path = os.path.join(source_directory, filename)

            # Remove quotes from the filename if present
            cleaned_filename = filename.strip("'\"")

            try:
                # Attempt to extract the date from the filename
                date_string = cleaned_filename.split("_")[-1].split(".")[0]
                file_date = datetime.strptime(date_string, "%Y%m%d")

                # Format the date into the desired directory name format YYYY-MM-DD
                destination_directory_name = file_date.strftime("%Y-%m-%d")

                # Create the destination directory path
                destination_directory = os.path.join(source_directory, destination_directory_name)

                # Check if the directory already exists
                if not os.path.exists(destination_directory):
                    # Create the directory if it doesn't exist
                    os.makedirs(destination_directory)
                    directories_created.add(destination_directory)
                    print(f"Created directory: {destination_directory}")

                # Move the file to the destination directory
                destination_path = os.path.join(destination_directory, cleaned_filename)
                shutil.move(file_path, destination_path)

                # Record the file movement for summary
                if destination_directory not in files_moved:
                    files_moved[destination_directory] = 1
                else:
                    files_moved[destination_directory] += 1
            except ValueError:
                # If the date string cannot be parsed into a valid date, skip the file
                print(f"Skipping file {filename} due to invalid date format.")

    # Print summary of operations
    for directory, count in files_moved.items():
        print(f"Moved {count} file(s) to {directory}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python archive.py <directory_path>")
        sys.exit(1)

    source_directory = sys.argv[1]

    # Check if the provided source directory exists
    if not os.path.isdir(source_directory):
        print(f"Error: {source_directory} is not a valid directory.")
        sys.exit(1)

    archive_files(source_directory)

