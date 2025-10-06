"""Direct test of CSV preview without API."""

import pandas as pd
import os

def preview_csv(file_path, rows=5):
    """Preview a CSV file."""
    # Remove quotes
    file_path = file_path.strip('"').strip("'")
    
    print(f"File path: {file_path}")
    print(f"File exists: {os.path.exists(file_path)}")
    
    if not os.path.exists(file_path):
        print(f"ERROR: File not found!")
        return
    
    print(f"\nReading {rows} rows...")
    try:
        df = pd.read_csv(file_path, nrows=rows)
        print(f"\nSuccess! Loaded {len(df)} rows, {len(df.columns)} columns")
        print(f"\nColumns: {df.columns.tolist()}")
        print(f"\nData:")
        print(df.to_string())
        
    except Exception as e:
        print(f"ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    file_path = r"C:\Users\mrunk\Downloads\FINAL_INFOSYS.csv"
    preview_csv(file_path, rows=5)
