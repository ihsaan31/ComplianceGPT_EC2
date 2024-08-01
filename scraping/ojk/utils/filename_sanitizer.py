import csv
import os
import shutil
import logging
import re
from datetime import datetime
from dateutil import parser
import locale

# Setup locale to Indonesian for date parsing
# locale.setlocale(locale.LC_TIME, 'id_ID.utf8')

# Setup logging
logging.basicConfig(filename='./log/filename_sanitizer.log', level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def convert_date_format(input_date):
    # Define a mapping of Indonesian month names to their numerical equivalents
    month_mapping = {
        'januari': '01',
        'februari': '02',
        'maret': '03',
        'april': '04',
        'mei': '05',
        'juni': '06',
        'juli': '07',
        'agustus': '08',
        'september': '09',
        'oktober': '10',
        'november': '11',
        'desember': '12'
    }

    # Split the input_date by space to extract day, month, and year
    parts = input_date.split()
    day = parts[0]
    month = parts[1].lower()  # Convert month to lowercase for case insensitivity
    year = parts[2]

    # Convert month name to numeric representation
    month_numeric = month_mapping.get(month, '00')  # '00' as default if month not found

    # Format the date as "01062024"
    formatted_date = f"{day.zfill(2)}{month_numeric}{year}"

    return formatted_date

def sanitize_filenames():
    # Paths
    source_csv = './log/ojk_document_scraping_result.csv'
    log_csv = './log/ojk_document_sanitizing_result.csv'
    source_dir = './data'
    destination_dir = './data_sanitized'

    # Create destination directory if not exists
    os.makedirs(destination_dir, exist_ok=True)

    # Read the source CSV
    with open(source_csv, 'r', encoding='utf-8') as src_file:
        reader = csv.DictReader(src_file)
        rows = list(reader)

    # Prepare log CSV with additional header
    if not os.path.exists(log_csv):
        with open(log_csv, 'w', newline='', encoding='utf-8') as log_file:
            fieldnames = reader.fieldnames + ['new_filename']
            writer = csv.DictWriter(log_file, fieldnames=fieldnames)
            writer.writeheader()

    # Process each row
    for row in rows:
        try:
            # Extract necessary fields
            title = row['filename']
            title = title.replace(' -- ', '_')
            title = re.sub(r'[./\- ,()]+', '_', title)
            jenis_regulasi = row['jenis_regulasi'].lower()
            jenis_regulasi = re.sub(r'[./\- ,()]+', '_', jenis_regulasi)
            nomor_regulasi = row['nomor_regulasi'].lower()
            nomor_regulasi = re.sub(r'[./\- ,()]+', '_', nomor_regulasi)
            tanggal_berlaku = row['tanggal_berlaku'].lower()
            tanggal_berlaku = convert_date_format(tanggal_berlaku)
            old_filename = row['filename']  
            ext = os.path.splitext(old_filename)[1]

            # Construct new filename
            new_filename = f"ojk-{jenis_regulasi}-{nomor_regulasi}-{tanggal_berlaku}-{title}"

            # Replace spaces with hyphens and remove invalid characters
            new_filename = new_filename.replace(" ", "-")
            new_filename = re.sub(r'[\\/*?:"<>.|]', '', new_filename)

            # Ensure the filename is not too long
            maxlen = 250 - len(ext)  # Max filename length in Windows
            if len(new_filename) > maxlen:
                new_filename = new_filename[:maxlen]

            new_filename = f"{new_filename}{ext}".lower()

            # Source and destination paths
            src_path = os.path.join(source_dir, old_filename)
            dest_path = os.path.join(destination_dir, new_filename)

            # Copy file to new destination
            shutil.copy2(src_path, dest_path)

            # Update row with new filename
            row['new_filename'] = new_filename

            # Log the successful operation
            logging.info(
                f"Successfully copied and renamed {old_filename} to {new_filename}")
            print(
                f"Successfully copied and renamed {old_filename} to {new_filename}")

            # Append row to log CSV
            with open(log_csv, 'a', newline='', encoding='utf-8') as log_file:
                writer = csv.DictWriter(
                    log_file, fieldnames=reader.fieldnames + ['new_filename'])
                writer.writerow(row)

        except Exception as e:
            logging.error(f"Failed to process {old_filename}: {e}")
            print(f"Failed to process {old_filename}: {e}")
