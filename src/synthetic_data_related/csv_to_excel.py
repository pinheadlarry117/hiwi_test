# src/csv_to_excel.py

from pathlib import Path
import pandas as pd

"""
def folder_to_excel(folder, excel_file):
    rows = []

    csv_files = sorted(
        Path(folder).glob("*.csv"),
        key=lambda p: int(p.stem)
    )

    for csv_file in csv_files:
        table_id = int(csv_file.stem)

        df = pd.read_csv(csv_file)

        for col_id, col_name in enumerate(df.columns, start=1):
            rows.append({
                "table id": table_id,
                "column id": col_id,
                "column name": col_name,
                "column": "",
                "content": "",
                "crossed": ""
            })

    pd.DataFrame(rows).to_excel(excel_file, index=False)
"""

def folder_to_excel(folder, output_excel):
    rows = []

    excel_files = sorted(Path(folder).glob("*.xlsx"))

    for excel_file in excel_files:
        table_name = excel_file.stem

        df = pd.read_excel(excel_file)

        for col_id, col_name in enumerate(df.columns, start=1):
            rows.append({
                "table name": table_name if col_id == 1 else "",
                "column id": col_id,
                "column name": col_name,
                "column": "",
                "content": "",
                "crossed": ""
            })

        # blank row between tables
        rows.append({
            "table name": "",
            "column id": "",
            "column name": "",
            "column": "",
            "content": "",
            "crossed": ""
        })

    metadata_df = pd.DataFrame(rows)
    metadata_df.to_excel(output_excel, index=False)