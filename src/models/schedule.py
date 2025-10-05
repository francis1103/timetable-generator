"""Schedule and timetable data structures."""

from dataclasses import dataclass, field
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
from .entities import Course, Faculty, Room, TimeSlot, Student


@dataclass
class ScheduleSlot:
    """Represents a single scheduled class session."""
    course: Course
    faculty: Faculty
    room: Room
    time_slot: TimeSlot
    students: Set[Student] = field(default_factory=set)
    slot_id: str = field(default="")
    
    def __post_init__(self):
        if not self.slot_id:
            self.slot_id = f"{self.course.course_id}_{self.time_slot.slot_id}_{self.room.room_id}"
    
    def __hash__(self):
        return hash(self.slot_id)
    
    def __eq__(self, other):
        if not isinstance(other, ScheduleSlot):
            return False
        return self.slot_id == other.slot_id
    
    def has_conflict_with(self, other: 'ScheduleSlot') -> Tuple[bool, List[str]]:
        """
        Check if this schedule slot conflicts with another.
        Returns (has_conflict, list_of_conflict_reasons).
        """
        conflicts = []
        
        # Check if time slots overlap
        if not self.time_slot.overlaps_with(other.time_slot):
            return False, []
        
        # Same room conflict
        if self.room == other.room:
            conflicts.append(f"Room {self.room.name} double-booked")
        
        # Same faculty conflict
        if self.faculty == other.faculty:
            conflicts.append(f"Faculty {self.faculty.name} has overlapping classes")
        
        # Student conflicts
        common_students = self.students & other.students
        if common_students:
            conflicts.append(f"{len(common_students)} students have overlapping classes")
        
        return len(conflicts) > 0, conflicts


@dataclass
class Timetable:
    """Represents a complete timetable for an institution."""
    schedule_slots: List[ScheduleSlot] = field(default_factory=list)
    metadata: Dict[str, any] = field(default_factory=dict)
    generation_timestamp: datetime = field(default_factory=datetime.now)
    conflicts: List[Tuple[ScheduleSlot, ScheduleSlot, List[str]]] = field(default_factory=list)
    fitness_scores: Dict[str, float] = field(default_factory=dict)
    
    def add_slot(self, slot: ScheduleSlot) -> bool:
        """Add a schedule slot to the timetable."""
        self.schedule_slots.append(slot)
        return True
    
    def remove_slot(self, slot: ScheduleSlot) -> bool:
        """Remove a schedule slot from the timetable."""
        if slot in self.schedule_slots:
            self.schedule_slots.remove(slot)
            return True
        return False
    
    def get_faculty_schedule(self, faculty: Faculty) -> List[ScheduleSlot]:
        """Get all schedule slots for a specific faculty member."""
        return [slot for slot in self.schedule_slots if slot.faculty == faculty]
    
    def get_student_schedule(self, student: Student) -> List[ScheduleSlot]:
        """Get all schedule slots for a specific student."""
        return [slot for slot in self.schedule_slots if student in slot.students]
    
    def get_room_schedule(self, room: Room) -> List[ScheduleSlot]:
        """Get all schedule slots for a specific room."""
        return [slot for slot in self.schedule_slots if slot.room == room]
    
    def get_slots_by_day(self, day) -> List[ScheduleSlot]:
        """Get all schedule slots for a specific day."""
        return [slot for slot in self.schedule_slots if slot.time_slot.day == day]
    
    def get_slots_by_time(self, time_slot: TimeSlot) -> List[ScheduleSlot]:
        """Get all schedule slots for a specific time slot."""
        return [slot for slot in self.schedule_slots if slot.time_slot == time_slot]
    
    def detect_conflicts(self) -> List[Tuple[ScheduleSlot, ScheduleSlot, List[str]]]:
        """
        Detect all conflicts in the current timetable.
        Returns list of (slot1, slot2, conflict_reasons).
        """
        conflicts = []
        n = len(self.schedule_slots)
        
        for i in range(n):
            for j in range(i + 1, n):
                slot1 = self.schedule_slots[i]
                slot2 = self.schedule_slots[j]
                has_conflict, reasons = slot1.has_conflict_with(slot2)
                
                if has_conflict:
                    conflicts.append((slot1, slot2, reasons))
        
        self.conflicts = conflicts
        return conflicts
    
    def is_valid(self) -> bool:
        """Check if the timetable has no conflicts."""
        conflicts = self.detect_conflicts()
        return len(conflicts) == 0
    
    def get_total_slots(self) -> int:
        """Get total number of scheduled slots."""
        return len(self.schedule_slots)
    
    def get_utilization_stats(self) -> Dict[str, float]:
        """Get resource utilization statistics."""
        if not self.schedule_slots:
            return {}
        
        # Room utilization
        rooms = set(slot.room for slot in self.schedule_slots)
        total_room_hours = sum(slot.time_slot.duration_minutes() / 60 
                              for slot in self.schedule_slots)
        
        # Faculty utilization
        faculty_hours = {}
        for slot in self.schedule_slots:
            fid = slot.faculty.faculty_id
            hours = slot.time_slot.duration_minutes() / 60
            faculty_hours[fid] = faculty_hours.get(fid, 0) + hours
        
        avg_faculty_hours = sum(faculty_hours.values()) / len(faculty_hours) if faculty_hours else 0
        
        return {
            'total_rooms_used': len(rooms),
            'total_room_hours': total_room_hours,
            'total_faculty': len(faculty_hours),
            'average_faculty_hours': avg_faculty_hours,
            'max_faculty_hours': max(faculty_hours.values()) if faculty_hours else 0,
            'min_faculty_hours': min(faculty_hours.values()) if faculty_hours else 0,
        }


@dataclass
class Schedule:
    """Wrapper for managing multiple timetables and scheduling operations."""
    current_timetable: Optional[Timetable] = None
    historical_timetables: List[Timetable] = field(default_factory=list)
    all_courses: Set[Course] = field(default_factory=set)
    all_faculty: Set[Faculty] = field(default_factory=set)
    all_students: Set[Student] = field(default_factory=set)
    all_rooms: Set[Room] = field(default_factory=set)
    all_time_slots: Set[TimeSlot] = field(default_factory=set)
    
    def set_current_timetable(self, timetable: Timetable):
        """Set the current active timetable."""
        if self.current_timetable:
            self.historical_timetables.append(self.current_timetable)
        self.current_timetable = timetable
    
    def rollback_to_previous(self) -> bool:
        """Rollback to the previous timetable."""
        if self.historical_timetables:
            self.current_timetable = self.historical_timetables.pop()
            return True
        return False
    
    def export_current(self, format: str = 'json') -> Dict:
        """Export current timetable in specified format."""
        if not self.current_timetable:
            return {}
        
        # Basic export structure
        export_data = {
            'generation_timestamp': self.current_timetable.generation_timestamp.isoformat(),
            'total_slots': self.current_timetable.get_total_slots(),
            'is_valid': self.current_timetable.is_valid(),
            'conflicts': len(self.current_timetable.conflicts),
            'fitness_scores': self.current_timetable.fitness_scores,
            'utilization': self.current_timetable.get_utilization_stats(),
            'schedule': []
        }
        
        for slot in self.current_timetable.schedule_slots:
            export_data['schedule'].append({
                'course_id': slot.course.course_id,
                'course_name': slot.course.name,
                'faculty_id': slot.faculty.faculty_id,
                'faculty_name': slot.faculty.name,
                'room_id': slot.room.room_id,
                'room_name': slot.room.name,
                'day': slot.time_slot.day.name,
                'start_time': slot.time_slot.start_time.strftime('%H:%M'),
                'end_time': slot.time_slot.end_time.strftime('%H:%M'),
                'student_count': len(slot.students)
            })
        
        return export_data
