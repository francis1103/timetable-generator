"""Core entity models for the scheduling system."""

from dataclasses import dataclass, field
from typing import List, Set, Optional, Dict
from enum import Enum
from datetime import time


class DayOfWeek(Enum):
    """Days of the week."""
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class RoomType(Enum):
    """Types of rooms available."""
    LECTURE_HALL = "lecture_hall"
    LABORATORY = "laboratory"
    SEMINAR_ROOM = "seminar_room"
    AUDITORIUM = "auditorium"
    COMPUTER_LAB = "computer_lab"
    WORKSHOP = "workshop"


@dataclass
class TimeSlot:
    """Represents a time slot in the schedule."""
    day: DayOfWeek
    start_time: time
    end_time: time
    slot_id: str = field(default="")
    
    def __post_init__(self):
        if not self.slot_id:
            self.slot_id = f"{self.day.name}_{self.start_time.strftime('%H%M')}_{self.end_time.strftime('%H%M')}"
    
    def overlaps_with(self, other: 'TimeSlot') -> bool:
        """Check if this time slot overlaps with another."""
        if self.day != other.day:
            return False
        return not (self.end_time <= other.start_time or self.start_time >= other.end_time)
    
    def duration_minutes(self) -> int:
        """Get duration in minutes."""
        delta = (self.end_time.hour * 60 + self.end_time.minute) - \
                (self.start_time.hour * 60 + self.start_time.minute)
        return delta
    
    def __hash__(self):
        return hash(self.slot_id)
    
    def __eq__(self, other):
        if not isinstance(other, TimeSlot):
            return False
        return self.slot_id == other.slot_id


@dataclass
class Department:
    """Represents an academic department."""
    dept_id: str
    name: str
    head_of_department: Optional[str] = None
    building: Optional[str] = None
    
    def __hash__(self):
        return hash(self.dept_id)


@dataclass
class Room:
    """Represents a physical room/venue."""
    room_id: str
    name: str
    capacity: int
    room_type: RoomType
    building: str
    floor: int
    facilities: Set[str] = field(default_factory=set)
    is_available: bool = True
    
    def can_accommodate(self, student_count: int) -> bool:
        """Check if room can accommodate given number of students."""
        return self.capacity >= student_count and self.is_available
    
    def has_facility(self, facility: str) -> bool:
        """Check if room has a specific facility."""
        return facility.lower() in {f.lower() for f in self.facilities}
    
    def __hash__(self):
        return hash(self.room_id)
    
    def __eq__(self, other):
        if not isinstance(other, Room):
            return False
        return self.room_id == other.room_id


@dataclass
class Faculty:
    """Represents a faculty member."""
    faculty_id: str
    name: str
    email: str
    department: Department
    specializations: Set[str] = field(default_factory=set)
    max_hours_per_week: int = 20
    max_consecutive_classes: int = 3
    unavailable_slots: Set[TimeSlot] = field(default_factory=set)
    preferred_slots: Set[TimeSlot] = field(default_factory=set)
    current_workload: int = 0
    
    def is_available(self, slot: TimeSlot) -> bool:
        """Check if faculty is available for a given time slot."""
        return slot not in self.unavailable_slots
    
    def prefers_slot(self, slot: TimeSlot) -> bool:
        """Check if faculty prefers a given time slot."""
        return slot in self.preferred_slots
    
    def can_teach_more(self) -> bool:
        """Check if faculty can take more classes."""
        return self.current_workload < self.max_hours_per_week
    
    def __hash__(self):
        return hash(self.faculty_id)
    
    def __eq__(self, other):
        if not isinstance(other, Faculty):
            return False
        return self.faculty_id == other.faculty_id


@dataclass
class Student:
    """Represents a student."""
    student_id: str
    name: str
    email: str
    department: Department
    year: int
    semester: int
    enrolled_courses: Set[str] = field(default_factory=set)
    max_subjects_per_day: int = 5
    unavailable_slots: Set[TimeSlot] = field(default_factory=set)
    preferred_slots: Set[TimeSlot] = field(default_factory=set)
    
    def is_available(self, slot: TimeSlot) -> bool:
        """Check if student is available for a given time slot."""
        return slot not in self.unavailable_slots
    
    def is_enrolled_in(self, course_id: str) -> bool:
        """Check if student is enrolled in a course."""
        return course_id in self.enrolled_courses
    
    def __hash__(self):
        return hash(self.student_id)
    
    def __eq__(self, other):
        if not isinstance(other, Student):
            return False
        return self.student_id == other.student_id


@dataclass
class Course:
    """Represents a course/subject."""
    course_id: str
    name: str
    code: str
    department: Department
    credits: int
    duration_minutes: int
    sessions_per_week: int
    required_room_type: RoomType
    required_facilities: Set[str] = field(default_factory=set)
    enrolled_students: Set[Student] = field(default_factory=set)
    assigned_faculty: Optional[Faculty] = None
    prerequisite_courses: Set[str] = field(default_factory=set)
    max_students: int = 100
    is_lab: bool = False
    
    def get_enrolled_count(self) -> int:
        """Get number of enrolled students."""
        return len(self.enrolled_students)
    
    def can_enroll_student(self, student: Student) -> bool:
        """Check if a student can enroll in this course."""
        return self.get_enrolled_count() < self.max_students
    
    def requires_facility(self, facility: str) -> bool:
        """Check if course requires a specific facility."""
        return facility.lower() in {f.lower() for f in self.required_facilities}
    
    def __hash__(self):
        return hash(self.course_id)
    
    def __eq__(self, other):
        if not isinstance(other, Course):
            return False
        return self.course_id == other.course_id
