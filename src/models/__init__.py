"""Data models for the timetable scheduling system."""

from .entities import Faculty, Student, Room, Course, TimeSlot, Department
from .schedule import Schedule, ScheduleSlot, Timetable
from .preferences import Preference, PreferenceType

__all__ = [
    'Faculty',
    'Student',
    'Room',
    'Course',
    'TimeSlot',
    'Department',
    'Schedule',
    'ScheduleSlot',
    'Timetable',
    'Preference',
    'PreferenceType',
]
