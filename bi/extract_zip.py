import os
import zipfile
from glob import glob

from utils.utils import slugify

extracted_dir = 'extracted_files'
os.makedirs(extracted_dir, exist_ok=True)

zfiles = glob('files/*.zip')

for zpath in zfiles:
    zip_file_name = os.path.basename(zpath)
    zip_file_base = slugify(os.path.splitext(zip_file_name)[0])
    
    with zipfile.ZipFile(zpath, 'r') as zip_ref:
        for member in zip_ref.namelist():
            if not member.endswith('/'):
                source = zip_ref.open(member)
                member_base_name = os.path.basename(member)
                final_file_name = f"{zip_file_base}-{member_base_name}"
                
                # Ensure the path length limit
                if len(final_file_name) > 250 - len(extracted_dir) - 1:
                    final_file_name = final_file_name[:250 - len(extracted_dir) - 1]
                
                target_path = os.path.join(extracted_dir, final_file_name)
                with open(target_path, "wb") as target:
                    with source:
                        target.write(source.read())
                        
    print(f"Extracted files from: {zpath} to {extracted_dir}")
