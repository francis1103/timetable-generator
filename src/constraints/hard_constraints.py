"""Hard constraint implementations."""

from typing import List, Tuple, Set, Dict
from .validators import HardConstraintValidator, ConstraintViolation
from src.models.schedule import Timetable, ScheduleSlot
from src.models.entities import DayOfWeek


class NoRoomOverlapConstraint(HardConstraintValidator):
    """Ensures no room is double-booked at the same time."""
    
    def __init__(self):
        super().__init__("No Room Overlap")
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate entire timetable for room overlaps."""
        violations = []
        
        # Group slots by room
        room_slots: Dict[str, List[ScheduleSlot]] = {}
        for slot in timetable.schedule_slots:
            room_id = slot.room.room_id
            if room_id not in room_slots:
                room_slots[room_id] = []
            room_slots[room_id].append(slot)
        
        # Check for overlaps in each room
        for room_id, slots in room_slots.items():
            for i in range(len(slots)):
                for j in range(i + 1, len(slots)):
                    if slots[i].time_slot.overlaps_with(slots[j].time_slot):
                        violations.append(ConstraintViolation(
                            constraint_name=self.name,
                            severity='hard',
                            description=f"Room {slots[i].room.name} is double-booked",
                            entities_involved=[
                                slots[i].course.code,
                                slots[j].course.code,
                                room_id
                            ],
                            penalty_score=float('inf'),
                            suggestion=f"Reassign one class to a different room or time"
                        ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate a single slot for room overlap."""
        violations = []
        
        for existing_slot in timetable.schedule_slots:
            if existing_slot == slot:
                continue
            
            if (existing_slot.room == slot.room and 
                existing_slot.time_slot.overlaps_with(slot.time_slot)):
                violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    severity='hard',
                    description=f"Room {slot.room.name} already occupied",
                    entities_involved=[
                        slot.course.code,
                        existing_slot.course.code,
                        slot.room.room_id
                    ],
                    penalty_score=float('inf')
                ))
        
        return len(violations) == 0, violations


class NoFacultyOverlapConstraint(HardConstraintValidator):
    """Ensures no faculty member has overlapping classes."""
    
    def __init__(self):
        super().__init__("No Faculty Overlap")
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate entire timetable for faculty overlaps."""
        violations = []
        
        # Group slots by faculty
        faculty_slots: Dict[str, List[ScheduleSlot]] = {}
        for slot in timetable.schedule_slots:
            faculty_id = slot.faculty.faculty_id
            if faculty_id not in faculty_slots:
                faculty_slots[faculty_id] = []
            faculty_slots[faculty_id].append(slot)
        
        # Check for overlaps for each faculty
        for faculty_id, slots in faculty_slots.items():
            for i in range(len(slots)):
                for j in range(i + 1, len(slots)):
                    if slots[i].time_slot.overlaps_with(slots[j].time_slot):
                        violations.append(ConstraintViolation(
                            constraint_name=self.name,
                            severity='hard',
                            description=f"Faculty {slots[i].faculty.name} has overlapping classes",
                            entities_involved=[
                                slots[i].course.code,
                                slots[j].course.code,
                                faculty_id
                            ],
                            penalty_score=float('inf'),
                            suggestion=f"Reschedule one class to a different time"
                        ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate a single slot for faculty overlap."""
        violations = []
        
        for existing_slot in timetable.schedule_slots:
            if existing_slot == slot:
                continue
            
            if (existing_slot.faculty == slot.faculty and 
                existing_slot.time_slot.overlaps_with(slot.time_slot)):
                violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    severity='hard',
                    description=f"Faculty {slot.faculty.name} already teaching",
                    entities_involved=[
                        slot.course.code,
                        existing_slot.course.code,
                        slot.faculty.faculty_id
                    ],
                    penalty_score=float('inf')
                ))
        
        return len(violations) == 0, violations


class NoStudentOverlapConstraint(HardConstraintValidator):
    """Ensures no student has overlapping classes."""
    
    def __init__(self):
        super().__init__("No Student Overlap")
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate entire timetable for student overlaps."""
        violations = []
        
        # Check each pair of slots for student overlaps
        n = len(timetable.schedule_slots)
        for i in range(n):
            for j in range(i + 1, n):
                slot1 = timetable.schedule_slots[i]
                slot2 = timetable.schedule_slots[j]
                
                if not slot1.time_slot.overlaps_with(slot2.time_slot):
                    continue
                
                # Find common students
                common_students = slot1.students & slot2.students
                if common_students:
                    violations.append(ConstraintViolation(
                        constraint_name=self.name,
                        severity='hard',
                        description=f"{len(common_students)} students have overlapping classes",
                        entities_involved=[
                            slot1.course.code,
                            slot2.course.code,
                            f"{len(common_students)} students"
                        ],
                        penalty_score=float('inf') * len(common_students),
                        suggestion=f"Reschedule one class to avoid student conflicts"
                    ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate a single slot for student overlap."""
        violations = []
        
        for existing_slot in timetable.schedule_slots:
            if existing_slot == slot:
                continue
            
            if existing_slot.time_slot.overlaps_with(slot.time_slot):
                common_students = existing_slot.students & slot.students
                if common_students:
                    violations.append(ConstraintViolation(
                        constraint_name=self.name,
                        severity='hard',
                        description=f"{len(common_students)} students have conflicts",
                        entities_involved=[
                            slot.course.code,
                            existing_slot.course.code
                        ],
                        penalty_score=float('inf') * len(common_students)
                    ))
        
        return len(violations) == 0, violations


class RoomCapacityConstraint(HardConstraintValidator):
    """Ensures room capacity is not exceeded."""
    
    def __init__(self):
        super().__init__("Room Capacity")
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate entire timetable for room capacity."""
        violations = []
        
        for slot in timetable.schedule_slots:
            student_count = len(slot.students)
            if student_count > slot.room.capacity:
                violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    severity='hard',
                    description=f"Room {slot.room.name} capacity exceeded",
                    entities_involved=[
                        slot.course.code,
                        slot.room.room_id,
                        f"{student_count}/{slot.room.capacity} students"
                    ],
                    penalty_score=float('inf'),
                    suggestion=f"Assign to a larger room (need capacity ≥ {student_count})"
                ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate a single slot for room capacity."""
        violations = []
        
        student_count = len(slot.students)
        if student_count > slot.room.capacity:
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                severity='hard',
                description=f"Room capacity exceeded: {student_count}/{slot.room.capacity}",
                entities_involved=[slot.course.code, slot.room.room_id],
                penalty_score=float('inf')
            ))
        
        return len(violations) == 0, violations


class FacultyAvailabilityConstraint(HardConstraintValidator):
    """Ensures faculty is available during assigned time slots."""
    
    def __init__(self):
        super().__init__("Faculty Availability")
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate entire timetable for faculty availability."""
        violations = []
        
        for slot in timetable.schedule_slots:
            if not slot.faculty.is_available(slot.time_slot):
                violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    severity='hard',
                    description=f"Faculty {slot.faculty.name} not available",
                    entities_involved=[
                        slot.faculty.faculty_id,
                        slot.course.code,
                        slot.time_slot.slot_id
                    ],
                    penalty_score=float('inf'),
                    suggestion=f"Reschedule to faculty's available time"
                ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate a single slot for faculty availability."""
        violations = []
        
        if not slot.faculty.is_available(slot.time_slot):
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                severity='hard',
                description=f"Faculty {slot.faculty.name} not available at this time",
                entities_involved=[slot.faculty.faculty_id, slot.time_slot.slot_id],
                penalty_score=float('inf')
            ))
        
        return len(violations) == 0, violations


class StudentAvailabilityConstraint(HardConstraintValidator):
    """Ensures students are available during assigned time slots."""
    
    def __init__(self):
        super().__init__("Student Availability")
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate entire timetable for student availability."""
        violations = []
        
        for slot in timetable.schedule_slots:
            unavailable_students = [
                s for s in slot.students 
                if not s.is_available(slot.time_slot)
            ]
            
            if unavailable_students:
                violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    severity='hard',
                    description=f"{len(unavailable_students)} students not available",
                    entities_involved=[
                        slot.course.code,
                        slot.time_slot.slot_id,
                        f"{len(unavailable_students)} students"
                    ],
                    penalty_score=float('inf') * len(unavailable_students),
                    suggestion=f"Reschedule to when all students are available"
                ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate a single slot for student availability."""
        violations = []
        
        unavailable_students = [
            s for s in slot.students 
            if not s.is_available(slot.time_slot)
        ]
        
        if unavailable_students:
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                severity='hard',
                description=f"{len(unavailable_students)} students unavailable",
                entities_involved=[slot.course.code],
                penalty_score=float('inf') * len(unavailable_students)
            ))
        
        return len(violations) == 0, violations


class MaxSubjectsPerDayConstraint(HardConstraintValidator):
    """Ensures students don't exceed maximum subjects per day."""
    
    def __init__(self):
        super().__init__("Max Subjects Per Day")
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate entire timetable for max subjects per day."""
        violations = []
        
        # Group slots by student and day
        student_day_courses: Dict[str, Dict[DayOfWeek, Set[str]]] = {}
        
        for slot in timetable.schedule_slots:
            for student in slot.students:
                sid = student.student_id
                if sid not in student_day_courses:
                    student_day_courses[sid] = {}
                
                day = slot.time_slot.day
                if day not in student_day_courses[sid]:
                    student_day_courses[sid][day] = set()
                
                student_day_courses[sid][day].add(slot.course.course_id)
        
        # Check each student's daily course count
        for student_id, day_courses in student_day_courses.items():
            for day, courses in day_courses.items():
                # Get student's max from schedule
                # For now, using a default of 5
                max_subjects = 5
                
                if len(courses) > max_subjects:
                    violations.append(ConstraintViolation(
                        constraint_name=self.name,
                        severity='hard',
                        description=f"Student has {len(courses)} subjects on {day.name}",
                        entities_involved=[
                            student_id,
                            day.name,
                            f"{len(courses)} courses"
                        ],
                        penalty_score=float('inf'),
                        suggestion=f"Redistribute courses across different days"
                    ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate a single slot for max subjects per day."""
        violations = []
        
        # Count courses for each student on this day
        for student in slot.students:
            courses_on_day = set()
            
            for existing_slot in timetable.schedule_slots:
                if existing_slot.time_slot.day == slot.time_slot.day:
                    if student in existing_slot.students:
                        courses_on_day.add(existing_slot.course.course_id)
            
            # Add current course
            courses_on_day.add(slot.course.course_id)
            
            max_subjects = getattr(student, 'max_subjects_per_day', 5)
            
            if len(courses_on_day) > max_subjects:
                violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    severity='hard',
                    description=f"Student exceeds max subjects on {slot.time_slot.day.name}",
                    entities_involved=[student.student_id, slot.course.code],
                    penalty_score=float('inf')
                ))
        
        return len(violations) == 0, violations
