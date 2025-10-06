"""Soft constraint implementations."""

from typing import List, Tuple, Dict, Set
from .validators import SoftConstraintValidator, ConstraintViolation
from src.models.schedule import Timetable, ScheduleSlot
from src.models.entities import DayOfWeek, TimeSlot
from datetime import time


class FacultyWorkloadBalanceConstraint(SoftConstraintValidator):
    """Ensures balanced workload distribution among faculty."""
    
    def __init__(self, ideal_hours: float = 15.0, weight: float = 1.0):
        super().__init__("Faculty Workload Balance", weight)
        self.ideal_hours = ideal_hours
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate workload balance across all faculty."""
        violations = []
        
        # Calculate hours for each faculty
        faculty_hours: Dict[str, float] = {}
        for slot in timetable.schedule_slots:
            fid = slot.faculty.faculty_id
            hours = slot.time_slot.duration_minutes() / 60.0
            faculty_hours[fid] = faculty_hours.get(fid, 0) + hours
        
        # Check deviation from ideal
        for fid, hours in faculty_hours.items():
            deviation = abs(hours - self.ideal_hours)
            
            if deviation > 5.0:  # More than 5 hours deviation
                penalty = deviation * 2.0
                violations.append(ConstraintViolation(
                    constraint_name=self.name,
                    severity='soft',
                    description=f"Faculty workload imbalance: {hours:.1f} hours (ideal: {self.ideal_hours})",
                    entities_involved=[fid],
                    penalty_score=penalty,
                    suggestion=f"Adjust to bring closer to {self.ideal_hours} hours/week"
                ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate workload for a specific slot."""
        # Calculate current workload for this faculty
        current_hours = 0
        for existing_slot in timetable.schedule_slots:
            if existing_slot.faculty == slot.faculty:
                current_hours += existing_slot.time_slot.duration_minutes() / 60.0
        
        # Add this slot
        current_hours += slot.time_slot.duration_minutes() / 60.0
        
        violations = []
        deviation = abs(current_hours - self.ideal_hours)
        
        if deviation > 5.0:
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                severity='soft',
                description=f"Workload would be {current_hours:.1f} hours",
                entities_involved=[slot.faculty.faculty_id],
                penalty_score=deviation * 2.0
            ))
        
        return len(violations) == 0, violations


class MinimizeTravelTimeConstraint(SoftConstraintValidator):
    """Minimizes travel time between consecutive classes."""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("Minimize Travel Time", weight)
        # Building distances (simplified - in real system, use actual distances)
        self.building_distances = {
            ('A', 'A'): 0,
            ('A', 'B'): 5,
            ('A', 'C'): 10,
            ('B', 'B'): 0,
            ('B', 'C'): 5,
            ('C', 'C'): 0,
        }
    
    def get_travel_time(self, building1: str, building2: str) -> float:
        """Get travel time in minutes between buildings."""
        key = tuple(sorted([building1, building2]))
        return self.building_distances.get(key, 10.0)  # Default 10 minutes
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate travel time for all consecutive classes."""
        violations = []
        
        # Group slots by faculty and sort by time
        faculty_slots: Dict[str, List[ScheduleSlot]] = {}
        for slot in timetable.schedule_slots:
            fid = slot.faculty.faculty_id
            if fid not in faculty_slots:
                faculty_slots[fid] = []
            faculty_slots[fid].append(slot)
        
        # Check consecutive classes for each faculty
        for fid, slots in faculty_slots.items():
            # Sort by day and time
            sorted_slots = sorted(slots, key=lambda s: (
                s.time_slot.day.value,
                s.time_slot.start_time
            ))
            
            for i in range(len(sorted_slots) - 1):
                current = sorted_slots[i]
                next_slot = sorted_slots[i + 1]
                
                # Check if on same day
                if current.time_slot.day != next_slot.time_slot.day:
                    continue
                
                # Check if consecutive (next starts when current ends)
                if current.time_slot.end_time == next_slot.time_slot.start_time:
                    travel_time = self.get_travel_time(
                        current.room.building,
                        next_slot.room.building
                    )
                    
                    if travel_time > 0:
                        violations.append(ConstraintViolation(
                            constraint_name=self.name,
                            severity='soft',
                            description=f"Consecutive classes in different buildings",
                            entities_involved=[
                                fid,
                                current.course.code,
                                next_slot.course.code
                            ],
                            penalty_score=travel_time,
                            suggestion=f"Schedule {travel_time} min break or use same building"
                        ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate travel time for a specific slot."""
        violations = []
        
        # Find adjacent slots for same faculty
        for existing_slot in timetable.schedule_slots:
            if existing_slot.faculty != slot.faculty:
                continue
            
            if existing_slot.time_slot.day != slot.time_slot.day:
                continue
            
            # Check if consecutive
            is_consecutive = (
                existing_slot.time_slot.end_time == slot.time_slot.start_time or
                slot.time_slot.end_time == existing_slot.time_slot.start_time
            )
            
            if is_consecutive:
                travel_time = self.get_travel_time(
                    existing_slot.room.building,
                    slot.room.building
                )
                
                if travel_time > 0:
                    violations.append(ConstraintViolation(
                        constraint_name=self.name,
                        severity='soft',
                        description=f"Requires {travel_time} min travel time",
                        entities_involved=[slot.faculty.faculty_id],
                        penalty_score=travel_time
                    ))
        
        return len(violations) == 0, violations


class TimePreferenceConstraint(SoftConstraintValidator):
    """Respects time preferences of faculty and students."""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("Time Preference", weight)
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate time preferences for all slots."""
        violations = []
        
        for slot in timetable.schedule_slots:
            # Check faculty preference
            if not slot.faculty.prefers_slot(slot.time_slot):
                if slot.time_slot in slot.faculty.preferred_slots:
                    penalty = 0  # Matches preference
                else:
                    penalty = 5.0  # Doesn't match preference
                    violations.append(ConstraintViolation(
                        constraint_name=self.name,
                        severity='soft',
                        description=f"Faculty {slot.faculty.name} prefers different time",
                        entities_involved=[slot.faculty.faculty_id, slot.course.code],
                        penalty_score=penalty,
                        suggestion="Schedule during faculty's preferred times"
                    ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate time preference for a specific slot."""
        violations = []
        
        if not slot.faculty.prefers_slot(slot.time_slot):
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                severity='soft',
                description="Not in faculty's preferred time",
                entities_involved=[slot.faculty.faculty_id],
                penalty_score=5.0
            ))
        
        return len(violations) == 0, violations


class SubjectSpacingConstraint(SoftConstraintValidator):
    """Ensures subjects are evenly spaced across the week."""
    
    def __init__(self, weight: float = 1.0):
        super().__init__("Subject Spacing", weight)
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate subject spacing for all courses."""
        violations = []
        
        # Group slots by course
        course_slots: Dict[str, List[ScheduleSlot]] = {}
        for slot in timetable.schedule_slots:
            cid = slot.course.course_id
            if cid not in course_slots:
                course_slots[cid] = []
            course_slots[cid].append(slot)
        
        # Check spacing for each course
        for cid, slots in course_slots.items():
            if len(slots) < 2:
                continue
            
            # Sort by day
            sorted_slots = sorted(slots, key=lambda s: s.time_slot.day.value)
            
            # Check consecutive days
            for i in range(len(sorted_slots) - 1):
                day_diff = (sorted_slots[i + 1].time_slot.day.value - 
                           sorted_slots[i].time_slot.day.value)
                
                if day_diff == 0:  # Same day
                    violations.append(ConstraintViolation(
                        constraint_name=self.name,
                        severity='soft',
                        description=f"Multiple sessions of same course on same day",
                        entities_involved=[cid, sorted_slots[i].time_slot.day.name],
                        penalty_score=10.0,
                        suggestion="Spread sessions across different days"
                    ))
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate subject spacing for a specific slot."""
        violations = []
        
        # Find other slots for same course
        same_course_slots = [
            s for s in timetable.schedule_slots
            if s.course == slot.course and s.time_slot.day == slot.time_slot.day
        ]
        
        if same_course_slots:
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                severity='soft',
                description="Same course already scheduled on this day",
                entities_involved=[slot.course.code],
                penalty_score=10.0
            ))
        
        return len(violations) == 0, violations


class ConsecutiveClassLimitConstraint(SoftConstraintValidator):
    """Limits number of consecutive classes for faculty."""
    
    def __init__(self, max_consecutive: int = 3, weight: float = 1.0):
        super().__init__("Consecutive Class Limit", weight)
        self.max_consecutive = max_consecutive
    
    def validate(self, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate consecutive class limits for all faculty."""
        violations = []
        
        # Group slots by faculty
        faculty_slots: Dict[str, List[ScheduleSlot]] = {}
        for slot in timetable.schedule_slots:
            fid = slot.faculty.faculty_id
            if fid not in faculty_slots:
                faculty_slots[fid] = []
            faculty_slots[fid].append(slot)
        
        # Check consecutive classes
        for fid, slots in faculty_slots.items():
            # Sort by day and time
            sorted_slots = sorted(slots, key=lambda s: (
                s.time_slot.day.value,
                s.time_slot.start_time
            ))
            
            consecutive_count = 1
            for i in range(len(sorted_slots) - 1):
                current = sorted_slots[i]
                next_slot = sorted_slots[i + 1]
                
                # Check if on same day and consecutive
                if (current.time_slot.day == next_slot.time_slot.day and
                    current.time_slot.end_time == next_slot.time_slot.start_time):
                    consecutive_count += 1
                    
                    if consecutive_count > self.max_consecutive:
                        violations.append(ConstraintViolation(
                            constraint_name=self.name,
                            severity='soft',
                            description=f"Faculty has {consecutive_count} consecutive classes",
                            entities_involved=[fid],
                            penalty_score=(consecutive_count - self.max_consecutive) * 5.0,
                            suggestion=f"Limit to {self.max_consecutive} consecutive classes"
                        ))
                else:
                    consecutive_count = 1
        
        return len(violations) == 0, violations
    
    def validate_slot(self, slot: ScheduleSlot, timetable: Timetable) -> Tuple[bool, List[ConstraintViolation]]:
        """Validate consecutive class limit for a specific slot."""
        violations = []
        
        # Count consecutive classes for this faculty on this day
        faculty_day_slots = [
            s for s in timetable.schedule_slots
            if s.faculty == slot.faculty and s.time_slot.day == slot.time_slot.day
        ]
        
        # Add current slot and sort
        faculty_day_slots.append(slot)
        sorted_slots = sorted(faculty_day_slots, key=lambda s: s.time_slot.start_time)
        
        # Find consecutive sequence containing this slot
        max_consecutive = 1
        current_consecutive = 1
        
        for i in range(len(sorted_slots) - 1):
            if sorted_slots[i].time_slot.end_time == sorted_slots[i + 1].time_slot.start_time:
                current_consecutive += 1
                max_consecutive = max(max_consecutive, current_consecutive)
            else:
                current_consecutive = 1
        
        if max_consecutive > self.max_consecutive:
            violations.append(ConstraintViolation(
                constraint_name=self.name,
                severity='soft',
                description=f"Would create {max_consecutive} consecutive classes",
                entities_involved=[slot.faculty.faculty_id],
                penalty_score=(max_consecutive - self.max_consecutive) * 5.0
            ))
        
        return len(violations) == 0, violations
