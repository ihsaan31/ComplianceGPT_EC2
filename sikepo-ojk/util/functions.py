import os
import glob
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC


def open_all_navbar(driver):
    while True:
        try:
            # Wait until the elements are present
            elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, ".dx-treeview-toggle-item-visibility:not(.dx-treeview-toggle-item-visibility-opened)"))
            )
            if len(elements) == 0:
                break
            
            # Iterate through and click each element
            for element in elements:
                try:
                    # Scroll to the element if necessary
                    driver.execute_script("arguments[0].scrollIntoView();", element)
                    driver.execute_script("arguments[0].click();", element)
                except Exception as e:
                    print(f"Could not click the element: {e}")
        except Exception as e:
            print(f"Finishing open all the section until it's leaf")
            break
        finally:
            print("Success")

# Function to parse the tree structure
def parse_tree(node):
    tree = {}
    for child in node.find_all('li', recursive=False):
        label = child.get('aria-label')
        item_id = child.get('data-item-id')
        subtree = child.find('ul')
        if subtree:
            tree[label] = {
                'data-item-id': item_id,
                'children': parse_tree(subtree)
            }
        else:
            tree[label] = {
                'data-item-id': item_id,
                'children': {}
            }
    return tree


def count_files(folder):
    count = 0
    for root, dirs, files in os.walk(folder):
        count += len([fn for fn in files if fn.endswith(".pdf")])
    return count


def new_file(cnt_files, DOWNLOAD_FOLDER):
    # Define the download folder path for Windows
    start = time.time()
    new_cnt_files = count_files(DOWNLOAD_FOLDER)
    while new_cnt_files <= cnt_files:
        new_cnt_files = count_files(DOWNLOAD_FOLDER)
        if time.time() - start >= 5:
             print("No files found in the download folder.")
             return None
    # Get list of all files in the download folder
    list_of_files = glob.glob(os.path.join(DOWNLOAD_FOLDER, "*"))

    # Check if the folder is not empty
    if list_of_files:
        # Find the most recently modified file
        latest_file = max(list_of_files, key=os.path.getctime)
        latest_filename = os.path.basename(latest_file)
        # Print the filename
        print(f"The latest downloaded file is: {latest_filename}")
    else:
        print("No files found in the download folder.")
    return latest_filename


def create_mapping(tree, mapping=None, parent_key=""):
    if mapping is None:
        mapping = {}
    for key, value in tree.items():
        if 'data-item-id' in value:
            mapping[key] = parent_key + key
        if 'children' in value:
            create_mapping(value['children'], mapping, parent_key + key + " ")
    return mapping


# Function to replace the keys in processed_data using the mapping
def replace_keys_in_data(data, mapping):
    replaced_data = {}
    for key, value in data.items():
        new_key = mapping.get(key, key)
        replaced_data[new_key] = value
    return replaced_data


def transform_string(input_string):
    # Split the string by spaces
    parts = input_string.split()
    
    # Initialize empty lists for the numbering and text parts
    numbers = []
    texts = []
    
    # Iterate over the parts to separate numbers and text
    before = None
    for part in parts:
        if part.replace('.', '').isdigit():
            numbers.append(part)
            before = 'digit'
        else:
            if before == 'text':
                texts[-1] = texts[-1] + " " + part
            else:
                texts.append(part)
            before = 'text'
    
    # The leaf numbering is the last numeric part
    leaf_numbering = numbers[-1]
    
    # Join the text parts with underscores
    concatenated_text = '_'.join(texts)
    
    # Combine the leaf numbering with the concatenated text
    result = f"{leaf_numbering} {concatenated_text}"
    return result


def change_form(dictionary):
    new_dic = {}
    for key, val in dictionary.items():
        new_key = transform_string(key)
        new_dic[new_key] = val
    
    return new_dic
