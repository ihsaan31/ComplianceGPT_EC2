import pandas as pd
import requests
import os
import random
import string
from urllib.parse import urlparse, unquote
from utils.constants import DATA_FINAL_PATH, UNSUCCESSFUL_DOWNLOADS_PATH

def get_file_extension(url, headers):
    if 'Content-Disposition' in headers:
        content_disposition = headers['Content-Disposition']
        if 'filename=' in content_disposition:
            filename = content_disposition.split('filename=')[-1].strip('"')
            return os.path.splitext(filename)[1]
  
    parsed_url = urlparse(url)
    path = unquote(parsed_url.path)
    extension = os.path.splitext(path)[1]
    
    return extension if extension else '.bin'

def add_random_chars(filename, length=3):
    random_chars = ''.join(random.choices(string.ascii_lowercase + string.digits, k=length))
    base, ext = os.path.splitext(filename)
    return f"{base}_{random_chars}{ext}"

def download_file(file_link, standardized_file_name, max_retries=10):
    extension = get_file_extension(file_link, {})
    standardized_file_name_with_extension = f"{standardized_file_name}{extension}"
    file_path = os.path.join('files', standardized_file_name_with_extension)

    # Ensure the filename does not exceed 250 characters
    if len(file_path) > 250:
        max_filename_length = 250 - len(os.path.join('files', '')) - len(extension)
        standardized_file_name_with_extension = f"{standardized_file_name[:max_filename_length]}{extension}"
        file_path = os.path.join('files', standardized_file_name_with_extension)

    # Add random characters to avoid filename conflicts
    file_path = add_random_chars(file_path)

    if os.path.exists(file_path):
        print(f"File already exists: {standardized_file_name_with_extension}. Skipping download.")
        return True

    attempts = 0
    while attempts < max_retries:
        try:
            response = requests.get(file_link, timeout=30)  # Adding a timeout for the request
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                return True
            else:
                print(f"Failed to download: {standardized_file_name_with_extension} from {file_link} (status code: {response.status_code})")
        except Exception as e:
            print(f"Error downloading {standardized_file_name_with_extension} from {file_link}: {e}")
        attempts += 1

    unsuccessful_downloads.append({
        "standardized_file_name": standardized_file_name,
        "file_link": file_link
    })
    return False

if __name__ == "__main__":
    os.makedirs('files', exist_ok=True)

    df = pd.read_csv(DATA_FINAL_PATH)
    unsuccessful_downloads = []

    for index, row in df.iterrows():
        download_file(row['file_link'], row['standardized_file_name'])

    unsuccessful_df = pd.DataFrame(unsuccessful_downloads)
    unsuccessful_df.to_csv(UNSUCCESSFUL_DOWNLOADS_PATH, index=False)

    print("Unsuccessful Downloads:")
    for file in unsuccessful_downloads:
        print(file["file_link"])
