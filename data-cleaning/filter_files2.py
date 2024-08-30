import os
import shutil
import csv
import requests
from bs4 import BeautifulSoup
from pydub import AudioSegment

# Get the directory where the script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Define paths relative to the script location
destination_dir = os.path.join(script_dir, "filtered-birds")
csv_file_path = os.path.join(script_dir, "names_and_codes.csv")

# Read bird species codes from the CSV file
bird_species_codes = {}
with open(csv_file_path, mode='r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        bird_species_codes[row['taxon_code']] = row['name']

# Ensure the destination directory exists
os.makedirs(destination_dir, exist_ok=True)

# Track missing bird species codes
missing_bird_species = set(bird_species_codes.keys())

# Function to scrape Xeno-canto for bird calls
def scrape_xeno_canto(bird_name, destination_folder):
    url = f"https://www.xeno-canto.org/explore?query=\"{bird_name}\""
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Find the audio file links
    audio_links = soup.find_all('a', href=True)
    audio_links = [link for link in audio_links if 'download' in link['href']]
    # print("audio links: ", audio_links)
    
    if not audio_links:
        print(f"No audio links found for {bird_name}.")
        return
    
    downloaded_files = 0
    consecutive_long_files = 0
    for i, link in enumerate(audio_links):
        if downloaded_files >= 15 or consecutive_long_files > 6:
            break
        
        href = link['href']
        if not href.startswith('http'):
            audio_url = f"https://www.xeno-canto.org{href}"
        else:
            audio_url = href
        audio_response = requests.get(audio_url)
        
        # Save the audio file temporarily
        temp_audio_file_path = os.path.join(destination_folder, f"temp_{bird_name}_{i+1}.mp3")
        with open(temp_audio_file_path, 'wb') as audio_file:
            audio_file.write(audio_response.content)
        
        # Check the duration of the audio file
        audio = AudioSegment.from_file(temp_audio_file_path)
        if len(audio) <= 15000:  # 15000 milliseconds = 15 seconds
            # Save the audio file permanently
            audio_file_path = os.path.join(destination_folder, f"{bird_name}_{downloaded_files+1}.mp3")
            shutil.move(temp_audio_file_path, audio_file_path)
            downloaded_files += 1
            consecutive_long_files = 0  # Reset the counter
            print(f"Downloaded {bird_name}_{downloaded_files}.mp3")
        else:
            os.remove(temp_audio_file_path)
            consecutive_long_files += 1
            print(f"Skipped {bird_name}_{i+1}.mp3 due to duration > 15 seconds")

# Iterate through the subdirectories in the destination directory
for folder_name in os.listdir(destination_dir):
    folder_path = os.path.join(destination_dir, folder_name)
    
    # Check if the folder name is in the list of bird species codes
    if os.path.isdir(folder_path) and folder_name in bird_species_codes:
        # Check if the folder is empty
        if not os.listdir(folder_path):
            # Print the empty folder
            print(f"Empty folder found for bird species: {folder_name}")
            # Scrape Xeno-canto for bird calls and save them in the folder
            scrape_xeno_canto(bird_species_codes[folder_name], folder_path)
        # Remove the found species from the missing list
        missing_bird_species.discard(folder_name)

# Print the missing bird species codes and create empty folders for them
for missing_species in missing_bird_species:
    print(f"Bird species not found: {missing_species}")
    # Create an empty folder for the missing species in the destination directory
    os.makedirs(os.path.join(destination_dir, missing_species), exist_ok=True)
    
    # Scrape Xeno-canto for bird calls and save them in the folder
    scrape_xeno_canto(bird_species_codes[missing_species], os.path.join(destination_dir, missing_species))

print("Empty bird folders have been populated with data successfully.")
print("Missing bird species have been printed and empty folders created.")