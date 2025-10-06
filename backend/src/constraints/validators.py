"""Base constraint validator classes."""

from abc import ABC, abstractmethod
from typing import List, Tuple, Dict, Any
from dataclasses import dataclass


@dataclass
class ConstraintViolation:
    """Represents a constraint violation."""
    constraint_name: str
    severity: str  # 'hard' or 'soft'
    description: str
    entities_involved: List[str]
    penalty_score: float = 0.0
    suggestion: str = ""


class ConstraintValidator(ABC):
    """Base class for all constraint validators."""
    
    def __init__(self, name: str, weight: float = 1.0):
        self.name = name
        self.weight = weight
        self.enabled = True
    
    @abstractmethod
    def validate(self, timetable: 'Timetable') -> Tuple[bool, List[ConstraintViolation]]:
        """
        Validate the constraint against a timetable.
        Returns (is_valid, list_of_violations).
        """
        pass
    
    @abstractmethod
    def validate_slot(self, slot: 'ScheduleSlot', timetable: 'Timetable') -> Tuple[bool, List[ConstraintViolation]]:
        """
        Validate a single schedule slot.
        Returns (is_valid, list_of_violations).
        """
        pass
    
    def get_penalty(self, violations: List[ConstraintViolation]) -> float:
        """Calculate penalty score for violations."""
        return sum(v.penalty_score for v in violations) * self.weight
    
    def enable(self):
        """Enable this constraint."""
        self.enabled = True
    
    def disable(self):
        """Disable this constraint."""
        self.enabled = False


class HardConstraintValidator(ConstraintValidator):
    """Base class for hard constraints that must never be violated."""
    
    def __init__(self, name: str):
        super().__init__(name, weight=float('inf'))  # Infinite weight for hard constraints
    
    def get_penalty(self, violations: List[ConstraintViolation]) -> float:
        """Hard constraint violations get infinite penalty."""
        if violations:
            return float('inf')
        return 0.0


class SoftConstraintValidator(ConstraintValidator):
    """Base class for soft constraints that should be optimized."""
    
    def __init__(self, name: str, weight: float = 1.0):
        super().__init__(name, weight)
    
    def get_penalty(self, violations: List[ConstraintViolation]) -> float:
        """Soft constraint violations get weighted penalties."""
        return super().get_penalty(violations)
    
    def calculate_satisfaction_score(self, timetable: 'Timetable') -> float:
        """
        Calculate how well the constraint is satisfied (0.0 to 1.0).
        Higher is better.
        """
        is_valid, violations = self.validate(timetable)
        if is_valid:
            return 1.0
        
        total_penalty = sum(v.penalty_score for v in violations)
        # Normalize to 0-1 range (implementation-specific)
        return max(0.0, 1.0 - (total_penalty / 100.0))
