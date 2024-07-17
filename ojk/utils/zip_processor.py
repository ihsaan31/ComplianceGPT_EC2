import os
import pandas as pd
import zipfile
from utils.new_document_scraper import href_to_filename

def extract_zip(zip_path, extract_dir):
    extracted_files = []
    zip_filename = os.path.basename(zip_path).rsplit('.', 1)[0]  # Get the zip filename without extension
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for member in zip_ref.namelist():
                # Skip directories
                if not member.endswith('/'):
                    # Rename the extracted file with the format "filename -- zipname.ext"
                    original_filename = os.path.basename(member)
                    original_filename_ext = original_filename.rsplit('.', 1)[1]
                    new_filename = f"{original_filename} -- {zip_filename}.{original_filename_ext}"
                    member_path = os.path.join(extract_dir, new_filename)
                    with open(member_path, 'wb') as extracted_file:
                        extracted_file.write(zip_ref.read(member))
                    extracted_files.append(new_filename)
    except zipfile.BadZipFile as e:
        print(f"Error extracting zip file {zip_path}: {e}")
    return extracted_files
    
def process_zip_files(df):
    document_data = []
    download_dir = './data_new_backup'
    output_csv = './log/ojk_document_scraping_result_new_backup.csv'

    # Load existing document data if the CSV file exists
    if os.path.exists(output_csv):
        existing_df = pd.read_csv(output_csv)
        existing_data = existing_df.values.tolist()
        document_data.extend(existing_data)

    for index, row in df.iterrows():
        zip_filename = row['filename']
        zip_path = os.path.join(download_dir, zip_filename)

        if os.path.exists(zip_path) and zip_path.endswith('.zip'):
            extracted_files = extract_zip(zip_path, download_dir)
            for extracted_file in extracted_files:
                document_data.append([row['title'], row['page_url'], row['tanggal_berlaku'], extracted_file, row['file_url']])

    # Save document data to CSV
    document_df = pd.DataFrame(document_data, columns=[
        'title', 'page_url', 'tanggal_berlaku', 'filename', 'file_url'])
    document_df.to_csv(output_csv, index=False)

    print("ZIP files have been processed and data saved to the CSV")
