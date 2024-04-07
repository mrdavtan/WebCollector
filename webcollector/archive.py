#!/bin/env python3

import os
import shutil
from datetime import datetime
import sys

def archive_files(source_directory):
    # Iterate over the files in the source directory
    for filename in os.listdir(source_directory):
        if filename.endswith(".json"):
            file_path = os.path.join(source_directory, filename)

            # Remove quotes from the filename if present
            cleaned_filename = filename.strip("'\"")

            try:
                # Extract the date from the filename
                date_string = cleaned_filename.split("_")[-2]
                file_date = datetime.strptime(date_string, "%Y%m%d").strftime("%Y-%m-%d")

                # Create the destination directory path
                destination_directory = os.path.join(source_directory, file_date)

                # Check if the directory already exists
                if not os.path.exists(destination_directory):
                    # Create the directory if it doesn't exist
                    os.makedirs(destination_directory)
                    print(f"Created directory: {destination_directory}")

                # Move the file to the destination directory
                destination_path = os.path.join(destination_directory, cleaned_filename)
                shutil.move(file_path, destination_path)
                print(f"Moved {cleaned_filename} to {destination_directory}")
            except ValueError:
                print(f"Skipping file {filename} due to invalid date format.")

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
