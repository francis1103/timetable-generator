"""Demo timetable test with predefined class duration and breaks."""

import requests
import json
import time
from datetime import datetime, timedelta

BASE_URL = "http://127.0.0.1:8000"
EXCEL_FILE = r"C:\Users\mrunk\Downloads\timetable_output.xlsx"

def get_demo_schedule_preferences():
    """Get demo schedule preferences."""
    print("\n" + "="*60)
    print("DEMO SCHEDULE CONFIGURATION")
    print("="*60)
    print("Using demo settings:")
    print("  Class Duration: 50 minutes")
    print("  Start Time: 09:00")
    print("  Break Duration: 15 minutes")
    print("  Lunch Duration: 45 minutes")
    print("  Assembly: Enabled (15 minutes)")
    print("="*60)
    
    return {
        'class_duration': 50,
        'start_time': '09:00',
        'break_duration': 15,
        'lunch_duration': 45,
        'assembly_enabled': True,
        'assembly_duration': 15
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
    print("TEST 1: Preview Excel Data with Custom Schedule & Breaks")
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
            
            # Display custom timetable with breaks
            print("CUSTOM TIMETABLE WITH BREAKS AND LUNCH:")
            print("=" * 120)
            
            # Display time schedule configuration
            print(f"⏰ Class Duration: {schedule_preferences['class_duration']} minutes")
            print(f"🍵 Break Duration: {schedule_preferences['break_duration']} minutes")
            print(f"🍽️ Lunch Duration: {schedule_preferences['lunch_duration']} minutes")
            print(f"🕘 Start Time: {schedule_preferences['start_time']}")
            print()
            
            # Show daily schedule for Monday as example
            course_data = preview['data']
            monday_data = course_data[0] if course_data else {}
            
            print("SAMPLE DAILY SCHEDULE (MONDAY):")
            print("-" * 80)
            print(f"{'Period':<18} {'Time Range':<15} {'Duration':<12} {'Course/Activity':<25}")
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
                        # If assembly was shown, first course period maps to Hour 1 (which was Assembly in data)
                        hour_col = f'Hour {period_idx}'
                        activity = monday_data.get(hour_col, 'Free Period')
                        if period_idx == 1 and activity == 'Assembly':
                            activity = monday_data.get('Hour 2', 'Free Period')  # Skip assembly, get next course
                    else:
                        hour_col = f'Hour {period_idx}'
                        activity = monday_data.get(hour_col, 'Free Period')
                    
                    period_display = f"📚 {period}"
                    period_idx += 1
                    if period_idx > 8:  # Max 8 course periods
                        break
                
                print(f"{period_display:<18} {time_range:<15} {duration:<12} {str(activity)[:25]:<25}")
            
            # Show complete weekly overview
            print(f"\n\nCOMPLETE WEEKLY SCHEDULE OVERVIEW:")
            print("=" * 120)
            
            for day_idx, day_row in enumerate(course_data):
                if day_idx >= 5:  # Show only first 5 days
                    break
                    
                day_name = day_row.get('Day', f'Day {day_idx+1}')
                print(f"\n📅 {day_name.upper()}:")
                print("-" * 60)
                
                # Show only class periods (no breaks in overview)
                for i in range(1, 9):  # Hours 1-8
                    hour_col = f'Hour {i}'
                    course = day_row.get(hour_col, 'Free')
                    
                    # Find corresponding time slot
                    class_periods = [item for item in time_schedule if item['period'].startswith('Period')]
                    if i <= len(class_periods):
                        time_info = class_periods[i-1]['time_range']
                        print(f"  Period {i} ({time_info}): {course}")
            
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
    """Run demo with predefined schedule preferences."""
    print("\n" + "="*80)
    print("AI TIMETABLE SCHEDULER - DEMO WITH BREAKS & CUSTOM DURATION")
    print("="*80)
    print(f"Target File: {EXCEL_FILE}")
    print(f"API Server: {BASE_URL}")
    print("="*80)
    
    # Get demo preferences
    preferences = get_demo_schedule_preferences()
    
    print(f"\n📅 SCHEDULE SUMMARY:")
    print(f"   ⏰ Class Duration: {preferences['class_duration']} minutes")
    print(f"   🕘 Start Time: {preferences['start_time']}")
    print(f"   🍵 Break Duration: {preferences['break_duration']} minutes")
    print(f"   🍽️ Lunch Duration: {preferences['lunch_duration']} minutes")
    
    if preferences.get('assembly_enabled', False):
        print(f"   🏫 Assembly: {preferences['assembly_duration']} minutes (Enabled)")
        total_periods = "8 classes + 3 breaks + 1 assembly"
    else:
        print(f"   🏫 Assembly: Disabled")
        total_periods = "8 classes + 3 breaks"
    
    print(f"   📊 Total Periods: {total_periods}")
    
    if not wait_for_server():
        print("\n⚠ Please start the server with: .\\start_api.ps1")
        return
    
    results = {
        "Preview Data with Breaks": test_preview(preferences),
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
    
    # Show break schedule summary
    schedule = generate_time_schedule(preferences)
    print(f"\n📋 DAILY SCHEDULE STRUCTURE:")
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