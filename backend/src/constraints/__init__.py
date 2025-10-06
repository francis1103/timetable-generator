"""Constraint validation system for hard and soft constraints."""

from .validators import ConstraintValidator, HardConstraintValidator, SoftConstraintValidator
from .hard_constraints import (
    NoRoomOverlapConstraint,
    NoFacultyOverlapConstraint,
    NoStudentOverlapConstraint,
    RoomCapacityConstraint,
    FacultyAvailabilityConstraint,
    StudentAvailabilityConstraint,
    MaxSubjectsPerDayConstraint,
)
from .soft_constraints import (
    FacultyWorkloadBalanceConstraint,
    MinimizeTravelTimeConstraint,
    TimePreferenceConstraint,
    SubjectSpacingConstraint,
    ConsecutiveClassLimitConstraint,
)

__all__ = [
    'ConstraintValidator',
    'HardConstraintValidator',
    'SoftConstraintValidator',
    'NoRoomOverlapConstraint',
    'NoFacultyOverlapConstraint',
    'NoStudentOverlapConstraint',
    'RoomCapacityConstraint',
    'FacultyAvailabilityConstraint',
    'StudentAvailabilityConstraint',
    'MaxSubjectsPerDayConstraint',
    'FacultyWorkloadBalanceConstraint',
    'MinimizeTravelTimeConstraint',
    'TimePreferenceConstraint',
    'SubjectSpacingConstraint',
    'ConsecutiveClassLimitConstraint',
]
