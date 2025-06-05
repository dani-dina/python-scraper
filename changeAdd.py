import pandas as pd
import ast

EXCEL_FILE = "members_final.xlsx"            # Your input Excel file
OUTPUT_FILE = "revised.xlsx"    # File to save with filled addresses
DICT_FILE = "name_address_map.txt"     # The file with the scraped dictionary

def load_address_dict(dict_file):
    with open(dict_file, "r", encoding="utf-8") as f:
        content = f.read()
        address_dict = ast.literal_eval(content.split("=", 1)[1].strip())
    return address_dict

def fill_addresses(excel_file, output_file, address_dict):
    df = pd.read_excel(excel_file)

    if 'Full Name' not in df.columns or 'Address' not in df.columns:
        raise ValueError("Excel file must have 'Name' and 'Address' columns.")

    filled_count = 0

    for idx, row in df.iterrows():
        name = row['Full Name']
        if pd.isna(row['Address']) and name in address_dict:
            df.at[idx, 'Address'] = address_dict[name]
            filled_count += 1

    df.to_excel(output_file, index=False)
    print(f"[Done] Filled {filled_count} missing addresses. Saved to '{output_file}'.")

if __name__ == "__main__":
    address_map = load_address_dict(DICT_FILE)
    fill_addresses(EXCEL_FILE, OUTPUT_FILE, address_map)
