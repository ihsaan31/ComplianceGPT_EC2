import pandas as pd
import requests
import os
from urllib.parse import urlparse, unquote
from utils.constants import DATA_FILE_PATH, UNSUCCESSFUL_DOWNLOADS_PATH
from utils.utils import slugify


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


def remove_extension(file_name):
    return os.path.splitext(file_name)[0]


def download_file(file_link, file_name, max_retries=3):
    base_file_name = remove_extension(file_name)
    sanitized_filename = slugify(base_file_name)
    download_filename = slugify(os.path.splitext(file_link.split('/')[-1])[0])
    extension = get_file_extension(file_link, {})
    final_filename = f"{sanitized_filename}-{download_filename}{extension}"
    file_path = os.path.join('files', final_filename)

    if len(file_path) > 255:
        print(f"File path too long: {file_path}")
        final_filename = f"{sanitized_filename[:50]}-{download_filename[:50]}{extension}"
        file_path = os.path.join('files', final_filename)

    if os.path.exists(file_path):
        print(f"File already exists: {final_filename}. Skipping download.")
        return True

    attempts = 0
    while attempts < max_retries:
        try:
            response = requests.get(file_link, timeout=30)  # Adding a timeout for the request
            if response.status_code == 200:
                with open(file_path, 'wb') as f:
                    f.write(response.content)
                print(f"Downloaded: {final_filename}")
                return True
            else:
                print(f"Failed to download: {file_name} from {file_link} (status code: {response.status_code})")
        except Exception as e:
            print(f"Error downloading {file_name} from {file_link}: {e}")
        attempts += 1

    unsuccessful_downloads.append({
        "file_name": file_name,
        "file_link": file_link
    })
    return False


if __name__ == "__main__":
  os.makedirs('files', exist_ok=True)

  df = pd.read_csv(DATA_FILE_PATH)
  unsuccessful_downloads = []

  for index, row in df.iterrows():
      download_file(row['file_link'], row['file_name'])

  unsuccessful_df = pd.DataFrame(unsuccessful_downloads)
  unsuccessful_df.to_csv(UNSUCCESSFUL_DOWNLOADS_PATH, index=False)

  print("Unsuccessful Downloads:")
  for file in unsuccessful_downloads:
      print(file["file_link"])
