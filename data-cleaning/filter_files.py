import os
import shutil
import csv
import logging

# Set up logging
logging.basicConfig(filename='missing_birds.log', level=logging.INFO, format='%(asctime)s - %(message)s')

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the script location
source_dir = os.path.join(script_dir, "old-birds")
destination_dir = os.path.join(script_dir, "filtered-birds")
csv_file_path = os.path.join(script_dir, "taxon_codes.csv")

# Read bird species codes from the CSV file
with open(csv_file_path, mode='r') as file:
    reader = csv.reader(file)
    bird_species_codes = {row[0] for row in reader}

# Ensure the destination directory exists
os.makedirs(destination_dir, exist_ok=True)

# Track missing bird species codes
missing_bird_species = set(bird_species_codes)

# Iterate through the subdirectories in the source directory
for folder_name in os.listdir(source_dir):
    folder_path = os.path.join(source_dir, folder_name)
    
    # Check if the folder name is in the list of bird species codes
    if os.path.isdir(folder_path) and folder_name in bird_species_codes:
        # Copy or move the folder to the destination directory
        shutil.copytree(folder_path, os.path.join(destination_dir, folder_name))
        # Remove the found species from the missing list
        missing_bird_species.discard(folder_name)

# Log the missing bird species codes and create empty folders for them
for missing_species in missing_bird_species:
    logging.info(f"Bird species not found: {missing_species}")
    # Create an empty folder for the missing species in the destination directory
    os.makedirs(os.path.join(destination_dir, missing_species), exist_ok=True)

print("Selected bird folders have been copied/moved successfully.")
print("Missing bird species have been logged and empty folders created.")