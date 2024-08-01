import os
import glob
import json

from fetch_data import fetch_data
from util.functions import create_mapping, replace_keys_in_data, transform_string, change_form
from util.constants import METADATA

def main():
    SECTION = "Bank Umum Syariah" # By default. You can change accordingly with sector that you need.
    result, tree_structure = fetch_data(SECTION)
    mapping = create_mapping(tree_structure)

    # Replace the keys in processed_data using the mapping
    replaced_data = replace_keys_in_data(result, mapping)
    new_form_data = change_form(replaced_data)

    with open(os.path.join(METADATA, f"{SECTION}.json"), "w") as outfile: 
        json.dump(new_form_data, outfile)

if __name__ == "__main__":
    main()

