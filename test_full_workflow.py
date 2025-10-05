"""Complete workflow test: Load data -> Generate schedule -> Export."""

import requests
import time
import os

BASE_URL = "http://127.0.0.1:8000"

def test_complete_workflow():
    """Test the complete timetabling workflow."""
    
    print("="*80)
    print("COMPLETE TIMETABLING WORKFLOW TEST")
    print("="*80)
    
    # Step 1: Load sample data
    print("\n[STEP 1] Loading sample data...")
    print("-"*80)
    
    response = requests.post(
        f"{BASE_URL}/api/load-data",
        params={
            "data_source": "data",  # Use the sample data directory
            "format": "csv"
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        print("✓ Data loaded successfully!")
        print(f"  Courses: {data['data']['courses']}")
        print(f"  Faculty: {data['data']['faculty']}")
        print(f"  Rooms: {data['data']['rooms']}")
        print(f"  Students: {data['data']['students']}")
    else:
        print(f"✗ Failed to load data: {response.text}")
        return
    
    # Step 2: Generate schedule
    print("\n[STEP 2] Generating optimal schedule...")
    print("-"*80)
    
    response = requests.post(
        f"{BASE_URL}/api/generate",
        json={
            "method": "nsga2",
            "population_size": 50,
            "num_generations": 20,
            "verbose": False
        }
    )
    
    if response.status_code == 200:
        result = response.json()
        timetable = result['timetable']
        print("✓ Schedule generated successfully!")
        print(f"  Total slots: {timetable['total_slots']}")
        print(f"  Valid: {timetable['is_valid']}")
        print(f"  Conflicts: {timetable['conflicts']}")
        print(f"  Fitness scores: {timetable.get('fitness_scores', 'N/A')}")
    else:
        print(f"✗ Failed to generate schedule: {response.text}")
        return
    
    # Step 3: Get statistics
    print("\n[STEP 3] Getting statistics...")
    print("-"*80)
    
    response = requests.get(f"{BASE_URL}/api/statistics")
    
    if response.status_code == 200:
        stats = response.json()['statistics']
        print("✓ Statistics retrieved!")
        if 'utilization' in stats:
            util = stats['utilization']
            print(f"  Rooms used: {util.get('rooms_used', 'N/A')}")
            print(f"  Faculty utilized: {util.get('faculty_utilized', 'N/A')}")
    
    # Step 4: Export to multiple formats
    print("\n[STEP 4] Exporting timetable...")
    print("-"*80)
    
    output_dir = r"C:\Users\mrunk\OneDrive\Desktop\excel generater"
    
    # Create directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    formats_to_export = ['json', 'html', 'excel']
    
    for fmt in formats_to_export:
        output_path = os.path.join(output_dir, f"timetable.{fmt if fmt != 'excel' else 'xlsx'}")
        
        response = requests.post(
            f"{BASE_URL}/api/export",
            params={
                "output_path": output_path,
                "format": fmt
            }
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"  ✓ Exported to {fmt.upper()}: {result['output_path']}")
        else:
            print(f"  ✗ Failed to export {fmt}: {response.text}")
    
    # Step 5: Get recommendations
    print("\n[STEP 5] Getting AI recommendations...")
    print("-"*80)
    
    response = requests.get(f"{BASE_URL}/api/recommendations")
    
    if response.status_code == 200:
        recs = response.json()['recommendations']
        print(f"✓ Retrieved {len(recs)} recommendations:")
        for i, rec in enumerate(recs[:5], 1):
            print(f"  {i}. {rec}")
    
    print("\n" + "="*80)
    print("WORKFLOW COMPLETED SUCCESSFULLY!")
    print("="*80)
    print(f"\nCheck your exported files at:")
    print(f"  {output_dir}")
    print("="*80)

if __name__ == "__main__":
    try:
        # Check if server is running
        response = requests.get(BASE_URL, timeout=2)
        if response.status_code != 200:
            print("Server is not responding correctly!")
            exit(1)
    except:
        print("ERROR: API server is not running!")
        print("Please start it with: .\\start_api.ps1")
        exit(1)
    
    test_complete_workflow()
