import os
import pandas as pd
import sqlite3

# Point directly to Django's active database in the root folder
db_name = "db.sqlite3"
conn = sqlite3.connect(db_name)

# Using exact PascalCase folder name
dataset_dir = "DataSetFiles"

file_mappings = {
    os.path.join(dataset_dir, "Allocated Limit for Honble MPs.xlsx"): ("allocated_limits", 1),
    os.path.join(dataset_dir, "Amount consented for Calamity.xlsx"): ("calamity_consents", 1),
    os.path.join(dataset_dir, "Works Recommended.xlsx"): ("works_recommended", 1),
    os.path.join(dataset_dir, "Works Sanctioned.xlsx"): ("works_sanctioned", 1),
    os.path.join(dataset_dir, "Works Completed.xlsx"): ("works_completed", 1),
    os.path.join(dataset_dir, "Expenditure on Completed and On-going Works as on Date.xlsx"): ("expenditure_logs", 1),
}

print("Starting clean data ingestion into Django database...")

for filepath, (table_name, header_row) in file_mappings.items():
    if os.path.exists(filepath):
        print(f"Reading {filepath}...")
        df = pd.read_excel(filepath, engine="calamine", header=header_row)
        
        # Clean column names
        df.columns = (
            df.columns.astype(str)
            .str.strip()
            .str.lower()
            .str.replace(r'[^0-9a-zA-Z]+', '_', regex=True)
            .str.strip('_')
        )
        
        # Write to SQLite database
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        print(f"Successfully loaded table: {table_name} ({len(df)} rows)")
    else:
        print(f"Warning: File not found -> {filepath}")

conn.close()
print("All tables successfully ingested into db.sqlite3!")