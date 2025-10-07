"""Interactive timetable test with assembly preferences."""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"
EXCEL_FILE = r"C:\Users\mrunk\Downloads\timetable_output.xlsx"

def get_user_schedule_preferences():
    """Get user input for schedule preferences including assembly."""
    print("\n" + "="*60)
    print("SCHEDULE CONFIGURATION")
    print("="*60)
    
    # Get class duration
    while True:
        try:
            duration = input("Enter class duration in minutes (30-120): ")
            duration = int(duration)
            if 30 <= duration <= 120:
                break
            else:
                print("Please enter a duration between 30 and 120 minutes.")
        except ValueError:
            print("Please enter a valid number.")
    
    # Get start time
    while True:
        try:
            start_time = input("Enter start time (HH:MM format, e.g., 09:00): ")
            datetime.strptime(start_time, "%H:%M")
            break
        except ValueError:
            print("Please enter time in HH:MM format (e.g., 09:00).")
    
    # Get assembly preferences
    print("\nAssembly Configuration:")
    while True:
        assembly_choice = input("Does your college have daily assembly? (y/n): ").lower().strip()
        if assembly_choice in ['y', 'yes', 'n', 'no']:
            assembly_enabled = assembly_choice in ['y', 'yes']
            break
        else:
            print("Please enter 'y' for yes or 'n' for no.")
    
    assembly_duration = 0
    if assembly_enabled:
        while True:
            try:
                assembly_duration = input("Enter assembly duration in minutes (5-20, default 15): ") or "15"
                assembly_duration = int(assembly_duration)
                if 5 <= assembly_duration <= 20:
                    break
                else:
                    print("Assembly duration must be between 5 and 20 minutes.")
            except ValueError:
                print("Please enter a valid number.")
    
    # Get break preferences
    print("\nBreak Configuration:")
    break_duration = input("Enter break duration in minutes (default 15): ") or "15"
    lunch_duration = input("Enter lunch duration in minutes (default 60): ") or "60"
    
    try:
        break_duration = int(break_duration)
        lunch_duration = int(lunch_duration)
    except ValueError:
        break_duration = 15
        lunch_duration = 60
    
    return {
        'class_duration': duration,
        'start_time': start_time,
        'break_duration': break_duration,
        'lunch_duration': lunch_duration,
        'assembly_enabled': assembly_enabled,
        'assembly_duration': assembly_duration
    }

def generate_time_schedule(preferences):
    """Generate time schedule with breaks, lunch, and optional assembly."""
    start_time = datetime.strptime(preferences['start_time'], "%H:%M")
    class_duration = preferences['class_duration']
    break_duration = preferences['break_duration']
    lunch_duration = preferences['lunch_duration']
    assembly_enabled = preferences.get('assembly_enabled', False)
    assembly_duration = preferences.get('assembly_duration', 0)
    
    schedule = []
    current_time = start_time
    period_count = 0
    
    # Add assembly if enabled
    if assembly_enabled and assembly_duration > 0:
        assembly_end = current_time + timedelta(minutes=assembly_duration)
        schedule.append({
            'period': 'ASSEMBLY',
            'time_range': f"{current_time.strftime('%H:%M')}-{assembly_end.strftime('%H:%M')}",
            'duration': f'{assembly_duration} min'
        })
        current_time = assembly_end
    
    # Generate 8 periods with breaks
    for i in range(8):
        period_count += 1
        end_time = current_time + timedelta(minutes=class_duration)
        
        schedule.append({
            'period': f'Period {period_count}',
            'time_range': f"{current_time.strftime('%H:%M')}-{end_time.strftime('%H:%M')}",
            'duration': f'{class_duration} min'
        })
        
        current_time = end_time
        
        # Add breaks
        if period_count == 2:  # After 2nd period - morning break
            break_end = current_time + timedelta(minutes=break_duration)
            schedule.append({
                'period': 'MORNING BREAK',
                'time_range': f"{current_time.strftime('%H:%M')}-{break_end.strftime('%H:%M')}",
                'duration': f'{break_duration} min'
            })
            current_time = break_end
            
        elif period_count == 4:  # After 4th period - lunch break
            lunch_end = current_time + timedelta(minutes=lunch_duration)
            schedule.append({
                'period': 'LUNCH BREAK',
                'time_range': f"{current_time.strftime('%H:%M')}-{lunch_end.strftime('%H:%M')}",
                'duration': f'{lunch_duration} min'
            })
            current_time = lunch_end
            
        elif period_count == 6:  # After 6th period - afternoon break
            break_end = current_time + timedelta(minutes=break_duration)
            schedule.append({
                'period': 'AFTERNOON BREAK',
                'time_range': f"{current_time.strftime('%H:%M')}-{break_end.strftime('%H:%M')}",
                'duration': f'{break_duration} min'
            })
            current_time = break_end
    
    return schedule

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

def test_preview(schedule_preferences):
    """Test the preview endpoint with custom schedule."""
    print("="*80)
    print("TEST 1: Preview Excel Data with Custom Schedule & Assembly")
    print("="*80)
    
    # Generate custom time schedule
    time_schedule = generate_time_schedule(schedule_preferences)
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/preview-data",
            params={
                "file_path": EXCEL_FILE,
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
            
            # Display custom timetable with assembly option
            print("CUSTOM TIMETABLE WITH ASSEMBLY & BREAKS:")
            print("=" * 120)
            
            # Display time schedule configuration
            print(f"⏰ Class Duration: {schedule_preferences['class_duration']} minutes")
            print(f"🍵 Break Duration: {schedule_preferences['break_duration']} minutes")
            print(f"🍽️ Lunch Duration: {schedule_preferences['lunch_duration']} minutes")
            print(f"🕘 Start Time: {schedule_preferences['start_time']}")
            
            if schedule_preferences.get('assembly_enabled', False):
                print(f"🏫 Assembly: {schedule_preferences['assembly_duration']} minutes (ENABLED)")
            else:
                print(f"🏫 Assembly: DISABLED")
            print()
            
            # Show daily schedule for Monday as example
            course_data = preview['data']
            monday_data = course_data[0] if course_data else {}
            
            print("SAMPLE DAILY SCHEDULE (MONDAY):")
            print("-" * 80)
            print(f"{'Period':<20} {'Time Range':<15} {'Duration':<12} {'Course/Activity':<25}")
            print("-" * 80)
            
            period_idx = 1
            assembly_shown = False
            
            for schedule_item in time_schedule:
                period = schedule_item['period']
                time_range = schedule_item['time_range']
                duration = schedule_item['duration']
                
                if period == 'ASSEMBLY':
                    activity = "Daily Assembly"
                    icon = "🏫"
                    period_display = f"{icon} {period}"
                    assembly_shown = True
                elif 'BREAK' in period or 'LUNCH' in period:
                    activity = period
                    icon = "🍵" if "BREAK" in period else "🍽️"
                    period_display = f"{icon} {period}"
                else:
                    # Map to course data - adjust for assembly
                    if assembly_shown:
                        # Skip assembly entry in data if we have our own assembly
                        hour_col = f'Hour {period_idx}'
                        activity = monday_data.get(hour_col, 'Free Period')
                        if period_idx == 1 and 'Assembly' in str(activity):
                            period_idx += 1  # Skip to next hour
                            hour_col = f'Hour {period_idx}'
                            activity = monday_data.get(hour_col, 'Free Period')
                    else:
                        hour_col = f'Hour {period_idx}'
                        activity = monday_data.get(hour_col, 'Free Period')
                    
                    period_display = f"📚 {period}"
                    period_idx += 1
                    if period_idx > 8:  # Max 8 course periods
                        break
                
                print(f"{period_display:<20} {time_range:<15} {duration:<12} {str(activity)[:25]:<25}")
            
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
    print("TEST 2: Load Excel Data")
    print("="*80)
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/load-data",
            params={
                "data_source": EXCEL_FILE
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
    """Run tests with user preferences including assembly."""
    print("\n" + "="*80)
    print("AI TIMETABLE SCHEDULER - INTERACTIVE CONFIGURATION")
    print("="*80)
    print(f"Target File: {EXCEL_FILE}")
    print(f"API Server: {BASE_URL}")
    print("="*80)
    
    # Get user preferences for schedule
    try:
        preferences = get_user_schedule_preferences()
    except KeyboardInterrupt:
        print("\n\nConfiguration cancelled by user.")
        return
    
    print(f"\n📅 SCHEDULE CONFIGURATION SUMMARY:")
    print(f"   ⏰ Class Duration: {preferences['class_duration']} minutes")
    print(f"   🕘 Start Time: {preferences['start_time']}")
    print(f"   🍵 Break Duration: {preferences['break_duration']} minutes")
    print(f"   🍽️ Lunch Duration: {preferences['lunch_duration']} minutes")
    
    if preferences.get('assembly_enabled', False):
        print(f"   🏫 Assembly: {preferences['assembly_duration']} minutes (ENABLED)")
        total_periods = "8 classes + 3 breaks + 1 assembly"
    else:
        print(f"   🏫 Assembly: DISABLED")
        total_periods = "8 classes + 3 breaks"
    
    print(f"   📊 Total Periods: {total_periods}")
    
    if not wait_for_server():
        print("\n⚠ Please start the server with: .\\start_api.ps1")
        return
    
    results = {
        "Preview Data with Assembly Config": test_preview(preferences),
        "Load Data": test_load()
    }
    
    # Summary
    print("\n" + "="*80)
    print("TEST SUMMARY")
    print("="*80)
    
    for test_name, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{test_name:<35} {status}")
    
    total_passed = sum(results.values())
    total_tests = len(results)
    
    print("="*80)
    print(f"Results: {total_passed}/{total_tests} tests passed")
    print("="*80)
    
    # Show final schedule structure
    schedule = generate_time_schedule(preferences)
    print(f"\n📋 FINAL DAILY SCHEDULE STRUCTURE:")
    print("-" * 50)
    for item in schedule:
        period = item['period']
        time_range = item['time_range']
        if period == 'ASSEMBLY':
            print(f"  🏫 {period}: {time_range}")
        elif 'Period' in period:
            print(f"  📚 {period}: {time_range}")
        else:
            icon = "🍵" if "MORNING" in period or "AFTERNOON" in period else "🍽️"
            print(f"  {icon} {period}: {time_range}")

if __name__ == "__main__":
    main()