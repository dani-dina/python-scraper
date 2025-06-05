import pandas as pd

file_path = "members_final.xlsx"  # Or your exact path if different
df = pd.read_excel(file_path)

# Clear the existing 'Address' column (with capital A)
if 'Address' in df.columns:
    df['Address'] = ''
    df.to_excel(file_path, index=False)
    print("[Success] 'Address' column cleared.")
else:
    print("[Error] No column named 'Address' found.")
