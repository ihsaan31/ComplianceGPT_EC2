import json
import os
import zipfile
from glob import glob
import pandas as pd

from utils.constants import DATA_FINAL_PATH
from utils.utils import slugify, format_title, remove_random_chars


extracted_dir = 'extracted_files'
os.makedirs(extracted_dir, exist_ok=True)

# Read the original data to match metadata
df = pd.read_csv(DATA_FINAL_PATH)
extracted_files_metadata = []

zfiles = glob('files/*.zip')

for zpath in zfiles:
    print("-" * 40)
    print("Original filename:", os.path.basename(zpath))
    
    zip_file_name_with_random_chars = os.path.basename(zpath)
    zip_file_name = remove_random_chars(zip_file_name_with_random_chars)  # Remove random chars and the extension
    zip_file_base = slugify(os.path.splitext(zip_file_name)[0])

    if not zip_file_name.endswith(".zip"):
        zip_file_name += ".zip"

    print("Processed zip filename:", zip_file_name)
    print("Zip base name:", zip_file_base)
    
    with zipfile.ZipFile(zpath, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if not member.endswith('/'):
                source = zip_ref.open(member)
                member_base_name = os.path.basename(member)
                formatted_member_base_name = format_title(member_base_name)
                print("Member base name:", formatted_member_base_name)
                
                final_file_name = f"{zip_file_base}-{formatted_member_base_name}"
                print("Pre-final filename:", final_file_name)
                
                # Ensure the path length limit
                if len(final_file_name) > 250 - len(extracted_dir) - 1:
                    final_file_name = final_file_name[:250 - len(extracted_dir) - 1]
                
                target_path = os.path.join(extracted_dir, final_file_name)
                with open(target_path, "wb") as target:
                    with source:
                        target.write(source.read())
                
                # Find the original row in the DataFrame
                matching_rows = df[df['standardized_file_name'].str.startswith(zip_file_name)]
                if not matching_rows.empty:
                    original_row = matching_rows.iloc[0]
                    
                    # Append metadata for the extracted file
                    extracted_files_metadata.append({
                        "title": original_row['title'],
                        "file_name": original_row['file_name'],
                        "file_link": original_row['file_link'],
                        "date": original_row['date'],
                        "type_of_regulation": original_row['type_of_regulation'],
                        "sector": original_row['sector'],
                        "standardized_file_name": original_row['standardized_file_name'],
                        "standardized_extracted_file_name": final_file_name
                    })
                else:
                    print(f"No matching metadata found for: {zip_file_name}")
                        
    print(f"Extracted files from: {zpath} to {extracted_dir}")

# Save the metadata to a JSON file
with open('extracted_files_metadata.json', 'w') as file:
    json.dump(extracted_files_metadata, file, indent=4)

print("Extracted files metadata saved to extracted_files_metadata.json")
