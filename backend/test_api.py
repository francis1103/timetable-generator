"""Test the API server (run this in a separate terminal after starting the API)."""

import requests
import json

BASE_URL = "http://localhost:8000"

def test_api():
    """Test the REST API endpoints."""
    
    print("Testing AI Timetable Scheduler API...")
    print("=" * 60)
    
    # Test 1: Root endpoint
    print("\n1. Testing root endpoint...")
    response = requests.get(f"{BASE_URL}/")
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()['name']}")
    
    # Test 2: Load data
    print("\n2. Loading data...")
    response = requests.post(
        f"{BASE_URL}/api/load-data",
        params={"data_source": "data", "format": "csv"}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()['data']
        print(f"   Courses: {data['courses']}")
        print(f"   Faculty: {data['faculty']}")
        print(f"   Rooms: {data['rooms']}")
    
    # Test 3: Generate schedule
    print("\n3. Generating schedule...")
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={"method": "nsga2", "verbose": False}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        result = response.json()['timetable']
        print(f"   Total slots: {result['total_slots']}")
        print(f"   Valid: {result['is_valid']}")
        print(f"   Conflicts: {result['conflicts']}")
    
    # Test 4: Get recommendations
    print("\n4. Getting AI recommendations...")
    response = requests.get(f"{BASE_URL}/api/recommendations")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        recs = response.json()['recommendations']
        for i, rec in enumerate(recs[:3], 1):
            print(f"   {i}. {rec}")
    
    # Test 5: Get statistics
    print("\n5. Getting statistics...")
    response = requests.get(f"{BASE_URL}/api/statistics")
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        stats = response.json()['statistics']
        print(f"   Total slots: {stats['total_slots']}")
        print(f"   Valid: {stats['is_valid']}")
    
    print("\n" + "=" * 60)
    print("API tests completed successfully!")

if __name__ == "__main__":
    try:
        test_api()
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to API server.")
        print("Please start the server first with:")
        print("  uvicorn src.api.main:app --reload")
