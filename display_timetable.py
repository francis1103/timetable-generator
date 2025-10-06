#!/usr/bin/env python3
"""Display the generated timetable in a formatted table."""

import json
from datetime import datetime

def display_timetable():
    # Load the timetable
    with open('output/timetable.json', 'r') as f:
        data = json.load(f)

    schedule = data['schedule']
    metadata = data['metadata']
    stats = data['statistics']
    fitness = data['fitness_scores']

    # Sort by day and time
    day_order = {'MONDAY': 1, 'TUESDAY': 2, 'WEDNESDAY': 3, 'THURSDAY': 4, 'FRIDAY': 5}
    schedule.sort(key=lambda x: (day_order[x['day']], x['start_time']))

    print('┌──────────┬──────────┬─────────────────────┬─────────────────────┬─────────────────┐')
    print('│   DAY    │   TIME   │       COURSE        │       FACULTY       │      ROOM       │')
    print('├──────────┼──────────┼─────────────────────┼─────────────────────┼─────────────────┤')

    for slot in schedule:
        day = slot['day'][:3]  # Abbreviate day
        time = f"{slot['start_time']}-{slot['end_time']}"
        course = slot['course']['name'][:19]  # Truncate if too long
        faculty = slot['faculty']['name'].split()[-1]  # Last name only
        room = slot['room']['name']
        
        print(f'│ {day:8} │ {time:8} │ {course:19} │ {faculty:19} │ {room:15} │')

    print('└──────────┴──────────┴─────────────────────┴─────────────────────┴─────────────────┘')
    print()
    
    # Course distribution
    course_count = {}
    for slot in schedule:
        course_name = slot['course']['name']
        course_count[course_name] = course_count.get(course_name, 0) + 1
    
    print('📊 COURSE DISTRIBUTION:')
    for course, count in course_count.items():
        print(f'• {course}: {count} sessions')
    print()
    
    print('🎯 OPTIMIZATION RESULTS:')
    print(f'• Hard Violations: {fitness["hard_violations"]} (Perfect!)')
    print(f'• Soft Penalty: {fitness["soft_penalty"]}')
    print(f'• Preference Score: {fitness["preference_score"]}')
    print()
    
    print('📈 UTILIZATION STATS:')
    print(f'• Total Rooms Used: {stats["total_rooms_used"]}')
    print(f'• Faculty Involved: {stats["total_faculty"]}')
    print(f'• Average Faculty Hours: {stats["average_faculty_hours"]}')
    print(f'• Total Room Hours: {stats["total_room_hours"]}')

if __name__ == "__main__":
    display_timetable()