"""Complete API test for FINAL_INFOSYS.csv file."""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"
CSV_FILE = r"C:\Users\mrunk\Downloads\FINAL_INFOSYS.csv"

def wait_for_server(max_attempts=10):
    """Wait for server to be ready."""
    print("Waiting for server to start...")
    for i in range(max_attempts):
        try:
            response = requests.get(BASE_URL, timeout=1)
            if response.status_code == 200:
                print("✓ Server is ready!\n")
                return True
        except:
            print(f"  Attempt {i+1}/{max_attempts}...")
            time.sleep(1)
    print("✗ Server did not start in time")
    return False

def test_preview():
    """Test the preview endpoint."""
    print("="*80)
    print("TEST 1: Preview CSV Data")
    print("="*80)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/preview-data",
            params={
                "file_path": CSV_FILE,
                "rows": 5
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            preview = data['preview']
            
            print(f"\n✓ SUCCESS!")
            print(f"\nFile: {preview['file_path']}")
            print(f"Columns ({preview['total_columns']}): {', '.join(preview['columns'])}")
            print(f"Rows shown: {preview['rows_shown']}\n")
            
            # Display data in table format
            print("Data Preview:")
            print("-" * 80)
            
            # Headers
            headers = preview['columns'][:5]  # Show first 5 columns
            print(f"{'Row':<5} " + " | ".join([f"{h[:15]:<15}" for h in headers]))
            print("-" * 80)
            
            # Data rows
            for idx, row in enumerate(preview['data']):
                values = [str(row.get(h, 'N/A'))[:15] for h in headers]
                print(f"{idx:<5} " + " | ".join([f"{v:<15}" for v in values]))
            
            return True
        else:
            print(f"\n✗ FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ EXCEPTION: {type(e).__name__}: {e}")
        return False

def test_load():
    """Test loading the data."""
    print("\n" + "="*80)
    print("TEST 2: Load CSV Data")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/load-data",
            params={
                "data_source": CSV_FILE
            },
            timeout=10
        )
        
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"\n✓ SUCCESS!")
            print(f"Message: {data['message']}")
            print(f"\nLoaded entities:")
            for key, count in data['data'].items():
                print(f"  - {key.capitalize()}: {count}")
            return True
        else:
            print(f"\n✗ FAILED!")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"\n✗ EXCEPTION: {type(e).__name__}: {e}")
        return False

def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("AI TIMETABLE SCHEDULER - API TESTS")
    print("="*80)
    print(f"Target File: {CSV_FILE}")
    print(f"API Server: {BASE_URL}")
    print("="*80 + "\n")
    
    if not wait_for_server():
        print("\n⚠ Please start the server with: .\\start_api.ps1")
        return
    
    results = {
        "Preview Data": test_preview(),
        "Load Data": test_load()
    }
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:<30} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print("="*80)
    print(f"Results: {total_passed}/{total_tests} tests passed")
    print("="*80)

if __name__ == "__main__":
    main()
