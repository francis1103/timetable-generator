"""Example usage script demonstrating the timetable scheduler."""

from pathlib import Path
from datetime import time

from src.models.entities import (
    Course, Faculty, Room, TimeSlot, Student, Department,
    DayOfWeek, RoomType
)
from src.optimization.scheduler import TimetableScheduler


def create_sample_data():
    """Create sample data for demonstration."""
    
    # Create departments
    cs_dept = Department(dept_id="CS", name="Computer Science")
    math_dept = Department(dept_id="MATH", name="Mathematics")
    
    # Create faculty
    faculty = [
        Faculty(
            faculty_id="F001",
            name="Dr. Alice Smith",
            email="alice@university.edu",
            department=cs_dept,
            specializations={"algorithms", "data structures"},
            max_hours_per_week=18
        ),
        Faculty(
            faculty_id="F002",
            name="Dr. Bob Johnson",
            email="bob@university.edu",
            department=cs_dept,
            specializations={"machine learning", "AI"},
            max_hours_per_week=20
        ),
        Faculty(
            faculty_id="F003",
            name="Dr. Carol Williams",
            email="carol@university.edu",
            department=math_dept,
            specializations={"calculus", "linear algebra"},
            max_hours_per_week=16
        ),
    ]
    
    # Create rooms
    rooms = [
        Room(
            room_id="R101",
            name="Room 101",
            capacity=50,
            room_type=RoomType.LECTURE_HALL,
            building="A",
            floor=1
        ),
        Room(
            room_id="R102",
            name="Room 102",
            capacity=30,
            room_type=RoomType.SEMINAR_ROOM,
            building="A",
            floor=1
        ),
        Room(
            room_id="L201",
            name="Lab 201",
            capacity=40,
            room_type=RoomType.COMPUTER_LAB,
            building="B",
            floor=2,
            facilities={"computers", "projector"}
        ),
    ]
    
    # Create students
    students = [
        Student(
            student_id=f"S{i:03d}",
            name=f"Student {i}",
            email=f"student{i}@university.edu",
            department=cs_dept,
            year=2,
            semester=3
        )
        for i in range(1, 51)
    ]
    
    # Create courses
    courses = [
        Course(
            course_id="CS101",
            name="Data Structures",
            code="CS101",
            department=cs_dept,
            credits=4,
            duration_minutes=60,
            sessions_per_week=3,
            required_room_type=RoomType.LECTURE_HALL,
            max_students=50
        ),
        Course(
            course_id="CS201",
            name="Machine Learning",
            code="CS201",
            department=cs_dept,
            credits=4,
            duration_minutes=60,
            sessions_per_week=2,
            required_room_type=RoomType.COMPUTER_LAB,
            max_students=40,
            is_lab=True
        ),
        Course(
            course_id="MATH301",
            name="Linear Algebra",
            code="MATH301",
            department=math_dept,
            credits=3,
            duration_minutes=60,
            sessions_per_week=2,
            required_room_type=RoomType.LECTURE_HALL,
            max_students=50
        ),
    ]
    
    # Enroll students in courses
    for course in courses:
        course.enrolled_students = set(students[:40])
        for student in students[:40]:
            student.enrolled_courses.add(course.course_id)
    
    # Assign faculty to courses
    courses[0].assigned_faculty = faculty[0]
    courses[1].assigned_faculty = faculty[1]
    courses[2].assigned_faculty = faculty[2]
    
    # Create time slots
    time_slots = []
    days = [DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY, 
            DayOfWeek.THURSDAY, DayOfWeek.FRIDAY]
    
    times = [
        (time(8, 0), time(9, 0)),
        (time(9, 0), time(10, 0)),
        (time(10, 0), time(11, 0)),
        (time(11, 0), time(12, 0)),
        (time(14, 0), time(15, 0)),
        (time(15, 0), time(16, 0)),
        (time(16, 0), time(17, 0)),
    ]
    
    for day in days:
        for start, end in times:
            time_slots.append(TimeSlot(day=day, start_time=start, end_time=end))
    
    return {
        'courses': courses,
        'faculty': faculty,
        'rooms': rooms,
        'time_slots': time_slots,
        'students': students
    }


def main():
    """Main demonstration function."""
    print("="*80)
    print("AI-Powered Timetable Scheduler - Demonstration")
    print("="*80)
    
    # Create sample data
    print("\n1. Creating sample data...")
    data = create_sample_data()
    print(f"   ✓ Created {len(data['courses'])} courses")
    print(f"   ✓ Created {len(data['faculty'])} faculty members")
    print(f"   ✓ Created {len(data['rooms'])} rooms")
    print(f"   ✓ Created {len(data['students'])} students")
    print(f"   ✓ Created {len(data['time_slots'])} time slots")
    
    # Initialize scheduler
    print("\n2. Initializing scheduler...")
    scheduler = TimetableScheduler()
    
    # Load data manually (since we have objects, not files)
    scheduler.courses = data['courses']
    scheduler.faculty = data['faculty']
    scheduler.rooms = data['rooms']
    scheduler.time_slots = data['time_slots']
    scheduler.students = data['students']
    print("   ✓ Scheduler initialized")
    
    # Add natural language rules
    print("\n3. Adding scheduling rules...")
    rules = [
        "No classes for Computer Science students after 3 PM on Fridays",
        "Dr. Alice Smith prefers morning slots",
        "Max 2 consecutive classes for all faculty"
    ]
    
    for rule in rules:
        print(f"   • {rule}")
    
    # Generate timetable using NSGA-II
    print("\n4. Generating optimal timetable using NSGA-II...")
    print("   (This may take a few moments...)\n")
    
    timetable = scheduler.generate_optimal_schedule(
        method='nsga2',
        verbose=True
    )
    
    # Display results
    print("\n5. Results Summary:")
    print(f"   Total Slots Scheduled: {timetable.get_total_slots()}")
    print(f"   Valid Schedule: {'✓ Yes' if timetable.is_valid() else '✗ No'}")
    print(f"   Number of Conflicts: {len(timetable.conflicts)}")
    
    stats = timetable.get_utilization_stats()
    print(f"\n6. Utilization Statistics:")
    print(f"   Rooms Used: {stats.get('total_rooms_used', 0)}")
    print(f"   Faculty Involved: {stats.get('total_faculty', 0)}")
    print(f"   Average Faculty Hours: {stats.get('average_faculty_hours', 0):.2f}")
    
    # Get conflict report
    if not timetable.is_valid():
        print("\n7. Conflict Analysis:")
        report = scheduler.get_conflict_report()
        print(f"   Total Conflicts: {report['total_conflicts']}")
        
        if report['conflicts_by_type']:
            print("\n   Conflicts by Type:")
            for conflict_type, count in report['conflicts_by_type'].items():
                print(f"      • {conflict_type}: {count}")
        
        # Attempt to resolve conflicts
        print("\n8. Attempting to resolve conflicts with ILP solver...")
        resolved = scheduler.resolve_conflicts()
        
        if resolved and resolved.is_valid():
            print("   ✓ All conflicts resolved!")
            timetable = resolved
        else:
            print("   ⚠ Some conflicts remain")
    
    # Get recommendations
    print("\n9. AI Recommendations:")
    recommendations = scheduler.get_recommendations()
    for i, rec in enumerate(recommendations, 1):
        print(f"   {i}. {rec}")
    
    # Export timetable
    print("\n10. Exporting timetable...")
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    
    scheduler.export(str(output_dir / "timetable.json"), format='json')
    print(f"   ✓ Exported to {output_dir / 'timetable.json'}")
    
    scheduler.export(str(output_dir / "timetable.html"), format='html')
    print(f"   ✓ Exported to {output_dir / 'timetable.html'}")
    
    scheduler.export(str(output_dir / "timetable.xlsx"), format='excel')
    print(f"   ✓ Exported to {output_dir / 'timetable.xlsx'}")
    
    print("\n" + "="*80)
    print("Demonstration Complete!")
    print("="*80)
    print(f"\nCheck the 'output' directory for exported files.")
    
    return timetable


if __name__ == "__main__":
    main()
