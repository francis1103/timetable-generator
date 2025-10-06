"""Preference and constraint preference models."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Any, Dict
from .entities import TimeSlot


class PreferenceType(Enum):
    """Types of preferences that can be specified."""
    TIME_PREFERENCE = "time_preference"
    ROOM_PREFERENCE = "room_preference"
    WORKLOAD_BALANCE = "workload_balance"
    CONSECUTIVE_CLASSES = "consecutive_classes"
    DAY_OFF = "day_off"
    MORNING_PREFERENCE = "morning_preference"
    EVENING_PREFERENCE = "evening_preference"
    BUILDING_PREFERENCE = "building_preference"
    NO_BACK_TO_BACK = "no_back_to_back"
    SUBJECT_SPACING = "subject_spacing"


class PreferencePriority(Enum):
    """Priority levels for preferences."""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class Preference:
    """Represents a scheduling preference (soft constraint)."""
    preference_id: str
    preference_type: PreferenceType
    priority: PreferencePriority
    entity_id: str  # ID of faculty/student/course
    entity_type: str  # 'faculty', 'student', 'course'
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    is_active: bool = True
    
    def __hash__(self):
        return hash(self.preference_id)
    
    def __eq__(self, other):
        if not isinstance(other, Preference):
            return False
        return self.preference_id == other.preference_id
    
    def get_weight(self) -> float:
        """Get the effective weight based on priority."""
        priority_weights = {
            PreferencePriority.LOW: 0.25,
            PreferencePriority.MEDIUM: 0.5,
            PreferencePriority.HIGH: 0.75,
            PreferencePriority.CRITICAL: 1.0
        }
        return self.weight * priority_weights.get(self.priority, 0.5)
    
    def satisfies(self, slot: 'ScheduleSlot') -> float:
        """
        Check how well a schedule slot satisfies this preference.
        Returns a score from 0.0 (not satisfied) to 1.0 (fully satisfied).
        """
        if not self.is_active:
            return 1.0
        
        # Default implementation - override for specific preference types
        return 0.5
    

@dataclass
class TimePreference(Preference):
    """Preference for specific time slots."""
    preferred_time_slots: set = field(default_factory=set)
    avoided_time_slots: set = field(default_factory=set)
    
    def __post_init__(self):
        self.preference_type = PreferenceType.TIME_PREFERENCE
    
    def satisfies(self, slot: 'ScheduleSlot') -> float:
        """Check if the time slot matches preferences."""
        if slot.time_slot in self.preferred_time_slots:
            return 1.0
        elif slot.time_slot in self.avoided_time_slots:
            return 0.0
        else:
            return 0.5


@dataclass
class WorkloadPreference(Preference):
    """Preference for balanced workload."""
    min_hours: float = 0
    max_hours: float = 20
    ideal_hours: float = 15
    
    def __post_init__(self):
        self.preference_type = PreferenceType.WORKLOAD_BALANCE
    
    def satisfies_workload(self, actual_hours: float) -> float:
        """Check how well actual hours match the preference."""
        if actual_hours < self.min_hours or actual_hours > self.max_hours:
            return 0.0
        elif actual_hours == self.ideal_hours:
            return 1.0
        else:
            # Linear interpolation
            if actual_hours < self.ideal_hours:
                range_size = self.ideal_hours - self.min_hours
                if range_size == 0:
                    return 1.0
                return (actual_hours - self.min_hours) / range_size
            else:
                range_size = self.max_hours - self.ideal_hours
                if range_size == 0:
                    return 1.0
                return 1.0 - ((actual_hours - self.ideal_hours) / range_size)
