#!/usr/bin/env python3
"""
Timetable Scheduling AI Input Structure Analysis
Shows how the system handles: Classrooms, Student Batches, Teachers, and Subjects
"""

import json
import pandas as pd
from collections import defaultdict

def analyze_input_structure():
    """Analyze and display the AI's input structure for timetable scheduling."""
    
    print("🎓 TIMETABLE SCHEDULING AI - INPUT STRUCTURE ANALYSIS")
    print("="*65)
    
    # Load the data files
    try:
        courses_df = pd.read_csv('data/courses.csv')
        faculty_df = pd.read_csv('data/faculty.csv')
        rooms_df = pd.read_csv('data/rooms.csv')
        students_df = pd.read_csv('data/students.csv')
    except Exception as e:
        print(f"Error loading data: {e}")
        return
    
    print("\n📚 1. COURSES/SUBJECTS INPUT")
    print("-" * 40)
    print(f"Total Subjects: {len(courses_df)}")
    print("Sample Course Structure:")
    print(courses_df.head(3).to_string(index=False))
    
    # Course analysis
    print(f"\nCourse Distribution by Department:")
    dept_courses = courses_df['department'].value_counts()
    for dept, count in dept_courses.items():
        print(f"  • {dept}: {count} courses")
    
    print(f"\nRoom Type Requirements:")
    room_types = courses_df['room_type'].value_counts()
    for room_type, count in room_types.items():
        print(f"  • {room_type}: {count} courses")
    
    print("\n👨‍🏫 2. TEACHERS/FACULTY INPUT")
    print("-" * 40)
    print(f"Total Faculty: {len(faculty_df)}")
    print("Sample Faculty Structure:")
    print(faculty_df[['name', 'department', 'specializations', 'max_hours_per_week']].head(3).to_string(index=False))
    
    # Faculty analysis
    print(f"\nFaculty Distribution by Department:")
    dept_faculty = faculty_df['department'].value_counts()
    for dept, count in dept_faculty.items():
        print(f"  • {dept}: {count} faculty members")
    
    print(f"\nFaculty Specializations:")
    all_specs = []
    for specs in faculty_df['specializations']:
        if pd.notna(specs):
            all_specs.extend([s.strip() for s in specs.split(';')])
    from collections import Counter
    spec_counts = Counter(all_specs)
    for spec, count in spec_counts.most_common(5):
        print(f"  • {spec}: {count} faculty")
    
    print("\n🏫 3. CLASSROOMS/ROOMS INPUT")
    print("-" * 40)
    print(f"Total Rooms: {len(rooms_df)}")
    print("Sample Room Structure:")
    print(rooms_df[['name', 'capacity', 'room_type', 'building', 'facilities']].head(3).to_string(index=False))
    
    # Room analysis
    print(f"\nRoom Types Available:")
    room_type_counts = rooms_df['room_type'].value_counts()
    for room_type, count in room_type_counts.items():
        print(f"  • {room_type}: {count} rooms")
    
    print(f"\nCapacity Distribution:")
    print(f"  • Average Capacity: {rooms_df['capacity'].mean():.1f}")
    print(f"  • Max Capacity: {rooms_df['capacity'].max()}")
    print(f"  • Min Capacity: {rooms_df['capacity'].min()}")
    
    print(f"\nBuilding Distribution:")
    building_counts = rooms_df['building'].value_counts()
    for building, count in building_counts.items():
        print(f"  • Building {building}: {count} rooms")
    
    print("\n👥 4. STUDENT BATCHES INPUT")
    print("-" * 40)
    print(f"Total Students: {len(students_df)}")
    print("Sample Student Structure:")
    print(students_df[['name', 'department', 'year', 'semester', 'enrolled_courses']].head(3).to_string(index=False))
    
    # Student analysis
    print(f"\nStudent Distribution by Department:")
    dept_students = students_df['department'].value_counts()
    for dept, count in dept_students.items():
        print(f"  • {dept}: {count} students")
    
    print(f"\nStudent Distribution by Year:")
    year_students = students_df['year'].value_counts().sort_index()
    for year, count in year_students.items():
        print(f"  • Year {year}: {count} students")
    
    # Course enrollment analysis
    print(f"\nCourse Enrollment Analysis:")
    all_enrollments = []
    for enrollments in students_df['enrolled_courses']:
        if pd.notna(enrollments):
            all_enrollments.extend([c.strip() for c in enrollments.split(';')])
    
    enrollment_counts = Counter(all_enrollments)
    print("Most Popular Courses:")
    for course, count in enrollment_counts.most_common(5):
        print(f"  • {course}: {count} students enrolled")
    
    print("\n🔗 5. RELATIONSHIP MAPPING")
    print("-" * 40)
    
    # Faculty-Subject mapping
    print("Faculty-Subject Specialization Mapping:")
    faculty_subject_map = {}
    for _, faculty in faculty_df.iterrows():
        specializations = faculty['specializations']
        if pd.notna(specializations):
            specs = [s.strip().lower() for s in specializations.split(';')]
            faculty_subject_map[faculty['name']] = specs
    
    # Course-Room requirement mapping
    print("\nCourse-Room Requirement Mapping:")
    course_room_map = {}
    for _, course in courses_df.iterrows():
        course_room_map[course['name']] = {
            'room_type': course['room_type'],
            'max_students': course['max_students'],
            'is_lab': bool(course['is_lab'])
        }
    
    # Display some mappings
    print("Sample Faculty-Specialization matches:")
    for faculty, specs in list(faculty_subject_map.items())[:3]:
        print(f"  • {faculty}: {', '.join(specs)}")
    
    print("\nSample Course-Room Requirements:")
    for course, req in list(course_room_map.items())[:3]:
        print(f"  • {course}: {req['room_type']} (capacity: {req['max_students']})")
    
    print("\n⚙️ 6. AI PROCESSING WORKFLOW")
    print("-" * 40)
    print("The AI processes these inputs through:")
    print("1. 📊 Data Validation & Preprocessing")
    print("   • Validate room capacities vs enrollment")
    print("   • Check faculty specializations vs courses")
    print("   • Verify student enrollment limits")
    print()
    print("2. 🎯 Constraint Generation")
    print("   • Hard: Room capacity, faculty availability")
    print("   • Soft: Preference matching, load balancing")
    print()
    print("3. 🧮 Optimization Algorithm (NSGA-II)")
    print("   • Multi-objective optimization")
    print("   • Constraint satisfaction")
    print("   • Preference maximization")
    print()
    print("4. 📋 Schedule Generation")
    print("   • Time slot assignment")
    print("   • Resource allocation")
    print("   • Conflict resolution")
    
    print("\n✅ 7. INPUT VALIDATION SUMMARY")
    print("-" * 40)
    
    # Validation checks
    validation_issues = []
    
    # Check if all courses have sufficient room capacity
    for _, course in courses_df.iterrows():
        suitable_rooms = rooms_df[
            (rooms_df['room_type'] == course['room_type']) & 
            (rooms_df['capacity'] >= course['max_students'])
        ]
        if len(suitable_rooms) == 0:
            validation_issues.append(f"No suitable room for {course['name']} (needs {course['room_type']} with {course['max_students']} capacity)")
    
    # Check faculty workload
    total_course_hours = courses_df['sessions_per_week'].sum()
    total_faculty_hours = faculty_df['max_hours_per_week'].sum()
    
    if validation_issues:
        print("⚠️ Validation Issues Found:")
        for issue in validation_issues[:3]:  # Show first 3 issues
            print(f"  • {issue}")
    else:
        print("✅ All inputs validated successfully!")
    
    print(f"\n📊 Resource Balance:")
    print(f"  • Total Course Hours Needed: {total_course_hours} hours/week")
    print(f"  • Total Faculty Hours Available: {total_faculty_hours} hours/week")
    print(f"  • Faculty Utilization Potential: {(total_course_hours/total_faculty_hours)*100:.1f}%")
    
    return {
        'courses': len(courses_df),
        'faculty': len(faculty_df),
        'rooms': len(rooms_df),
        'students': len(students_df),
        'validation_issues': len(validation_issues)
    }

if __name__ == "__main__":
    from collections import Counter
    analyze_input_structure()