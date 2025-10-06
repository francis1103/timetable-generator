"""Test the API with the FINAL_INFOSYS.csv file."""

import requests
from urllib.parse import quote

BASE_URL = "http://127.0.0.1:8000"

def test_preview_and_load():
    """Test preview and load data from custom CSV file."""
    
    print("Testing Custom CSV File...")
    print("=" * 80)
    
    # Your file path
    file_path = r"C:\Users\mrunk\Downloads\FINAL_INFOSYS.csv"
    
    # Test 1: Preview the data first
    print("\n1. Previewing top 5 rows...")
    print("-" * 80)
    
    # Properly encode the file path for URL
    encoded_path = quote(file_path)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/preview-data",
            params={"file_path": file_path, "rows": 5}
        )
        
        if response.status_code == 200:
            preview = response.json()['preview']
            print(f"File: {preview['file_path']}")
            print(f"Columns ({preview['total_columns']}): {', '.join(preview['columns'])}")
            print(f"\nFirst {preview['rows_shown']} rows:")
            print("-" * 80)
            
            # Print table header
            print(f"{'Index':<8} " + " | ".join([f"{col:<15}" for col in preview['columns'][:5]]))
            print("-" * 80)
            
            # Print data rows
            for idx, row in enumerate(preview['data']):
                values = [str(row.get(col, 'N/A'))[:15] for col in preview['columns'][:5]]
                print(f"{idx:<8} " + " | ".join([f"{val:<15}" for val in values]))
            
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
    
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Please start the server first with:")
        print("  uvicorn src.api.main:app --reload")
        return
    except Exception as e:
        print(f"Error: {e}")
        return
    
    # Test 2: Load the data (format auto-detected from .csv extension)
    print("\n\n2. Loading data into scheduler...")
    print("-" * 80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/load-data",
            params={"data_source": file_path}  # format auto-detected
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"Status: {result['status']}")
            print(f"Message: {result['message']}")
            print(f"\nLoaded entities:")
            for key, count in result['data'].items():
                print(f"  - {key.capitalize()}: {count}")
        else:
            print(f"Error: {response.status_code}")
            print(response.json())
    
    except Exception as e:
        print(f"Error: {e}")
    
    print("\n" + "=" * 80)
    print("Tests completed!")


def show_curl_examples():
    """Show correct curl command examples."""
    print("\n" + "=" * 80)
    print("CORRECT API USAGE EXAMPLES:")
    print("=" * 80)
    
    file_path = r"C:\Users\mrunk\Downloads\FINAL_INFOSYS.csv"
    
    print("\n1. Preview data (GET request):")
    print("-" * 80)
    print(f"""curl -X 'GET' \\
  '{BASE_URL}/api/preview-data?file_path={quote(file_path)}&rows=5' \\
  -H 'accept: application/json'""")
    
    print("\n2. Load data (POST request):")
    print("-" * 80)
    print(f"""curl -X 'POST' \\
  '{BASE_URL}/api/load-data?data_source={quote(file_path)}' \\
  -H 'accept: application/json' \\
  -d ''""")
    
    print("\n3. Load from directory (multiple CSV files):")
    print("-" * 80)
    print(f"""curl -X 'POST' \\
  '{BASE_URL}/api/load-data?data_source=data&format=csv' \\
  -H 'accept: application/json' \\
  -d ''""")
    
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_preview_and_load()
    show_curl_examples()
