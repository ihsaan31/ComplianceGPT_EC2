# Bank Indonesia Regulations Scraping
The scripts provided below allows users to scrape all regulations from Bank Indonesia.

# Objective

1. Retrieve PDF Regulations from BI Website: Regulation (bi.go.id). (Include all atachment for each regulation No.)

2. Retrieve the glossary from BI: Glosarium (bi.go.id). 

3. Create an excel/csv to log/track the scraping progress, including: 

- Regulation No

- Year of Regulation

- Sector/Subsector (if available) 

- PDF Title

- PDF Link

# Folder Structure

```
.
├── chromedriver/
│   └── chromedriver.exe
├── csv/
│   └── *.csv
├── extracted_files/
│   ├── *.pdf
│   ├── *.xlsx
│   └── *.docx
├── files/
│   ├── *.pdf
│   ├── *.xlsx
│   ├── *.docx
│   └── *.zip
├── utils/
│   ├── constants.py
│   └── utils.py
├── *.py
├── *.ipynb
├── README.md
└── requirements.txt
```

# Guide

`pip install -r "requirements.txt"`

Run the scripts in the following order:

1. fetch_regulations.py
2. check_last_page.py
3. fetch_regulation_detail.py
4. download_files.py
5. extract_zip.py
6. fetch_glosarium.ipynb

## fetch_regulations.py
This script will iterate all the regulations provided [here](https://www.bi.go.id/en/publikasi/peraturan/Default.aspx) and save the title and link to a .csv file.

## check_last_page.py
This script will halt at the last page of the list so the user may verify if they have completely scraped the entirety of the list.

## fetch_regulation_detail.py
This script will scrape the details of each regulation from the .csv file and then save it to another .csv file.

## download_files.py
This script will iterate the csv created by fetch_regulation_detail.py and download all of the attachments provided there.

## extract_zip.py
This script will automatically extract the contents of all .zip files including inside of subfolders.

## fetch_glosarium.ipynb
This script will fetch BI's glosarium page and return a .csv file

# Contributors
Arkan Alexei Andrei