import pandas as pd
import fitz
import os
import shutil

def is_scanned_pdf(pdf_path):
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text = page.get_text("text")
            if text.strip():
                return False
        return True
    except Exception as e:
        print(f"Error processing {pdf_path}: {e}")
        return False

def list_scanned_pdfs():
    folder_path = 'data_sanitized'
    scanned_pdfs = []
    for filename in os.listdir(folder_path):
        if filename.endswith('.pdf'):
            pdf_path = os.path.join(folder_path, filename)
            if is_scanned_pdf(pdf_path):
                scanned_pdfs.append(filename)
    return scanned_pdfs

def copy_scanned_pdfs():
    source_folder = 'data_sanitized'
    destination_folder = 'data_scanned_pdf'
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    scanned_pdfs = list_scanned_pdfs()
    for pdf in scanned_pdfs:
        source_path = os.path.join(source_folder, pdf)
        destination_path = os.path.join(destination_folder, pdf)
        shutil.copy2(source_path, destination_path)

def add_ocr_column_to_csv():
    csv_path = './log/ojk_document_sanitizing_result.csv'
    df = pd.read_csv(csv_path)
    ocr_status = []

    for filename in df['new_filename']:
        pdf_path = os.path.join('data_sanitized', filename)
        ocr_status.append(is_scanned_pdf(pdf_path))

    df['is_ocr'] = ocr_status
    df.to_csv(csv_path, index=False)