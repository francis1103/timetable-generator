"""Constraint Satisfaction Problem solver for timetable generation."""

from typing import List, Dict, Set, Optional, Tuple, Any
from constraint import Problem, Variable, AllDifferentConstraint, FunctionConstraint
import itertools

from src.models.entities import Course, Faculty, Room, TimeSlot, Student
from src.models.schedule import Timetable, ScheduleSlot


class CSPSolver:
    """
    Constraint Satisfaction Problem solver for timetabling.
    Enforces hard constraints during schedule generation.
    """
    
    def __init__(self,
                 courses: List[Course],
                 faculty: List[Faculty],
                 rooms: List[Room],
                 time_slots: List[TimeSlot],
                 students: List[Student]):
        """
        Initialize CSP solver.
        
        Args:
            courses: List of courses to schedule
            faculty: List of available faculty
            rooms: List of available rooms
            time_slots: List of available time slots
            students: List of students
        """
        self.courses = courses
        self.faculty_list = faculty
        self.rooms = rooms
        self.time_slots = time_slots
        self.students = students
        
        self.problem = Problem()
        self._build_csp()
    
    def _build_csp(self):
        """Build the constraint satisfaction problem."""
        # Create variables for each course session
        self.variables = {}
        
        for course in self.courses:
            for session in range(course.sessions_per_week):
                var_name = f"{course.course_id}_session_{session}"
                
                # Domain: (faculty, room, timeslot) tuples
                domain = []
                
                for faculty in self.faculty_list:
                    # Check if faculty can teach this course
                    if not self._faculty_can_teach(faculty, course):
                        continue
                    
                    for room in self.rooms:
                        # Check if room is suitable
                        if not self._room_is_suitable(room, course):
                            continue
                        
                        for timeslot in self.time_slots:
                            # Check basic availability
                            if faculty.is_available(timeslot):
                                domain.append((faculty, room, timeslot))
                
                if domain:
                    self.problem.addVariable(var_name, domain)
                    self.variables[var_name] = {
                        'course': course,
                        'session': session
                    }
        
        # Add constraints
        self._add_constraints()
    
    def _faculty_can_teach(self, faculty: Faculty, course: Course) -> bool:
        """Check if faculty can teach the course."""
        # Same department or has specialization
        return (faculty.department == course.department or
                any(spec.lower() in course.name.lower() 
                    for spec in faculty.specializations))
    
    def _room_is_suitable(self, room: Room, course: Course) -> bool:
        """Check if room is suitable for the course."""
        # Check room type and capacity
        return (room.room_type == course.required_room_type and
                room.capacity >= course.get_enrolled_count())
    
    def _add_constraints(self):
        """Add all CSP constraints."""
        # No room conflicts
        self._add_room_conflict_constraints()
        
        # No faculty conflicts
        self._add_faculty_conflict_constraints()
        
        # No student conflicts
        self._add_student_conflict_constraints()
    
    def _add_room_conflict_constraints(self):
        """Ensure no room is double-booked."""
        var_names = list(self.variables.keys())
        
        for i in range(len(var_names)):
            for j in range(i + 1, len(var_names)):
                var1, var2 = var_names[i], var_names[j]
                
                def no_room_conflict(assignment1, assignment2):
                    faculty1, room1, timeslot1 = assignment1
                    faculty2, room2, timeslot2 = assignment2
                    
                    # If different rooms or non-overlapping times, no conflict
                    if room1 != room2:
                        return True
                    
                    return not timeslot1.overlaps_with(timeslot2)
                
                self.problem.addConstraint(
                    FunctionConstraint(no_room_conflict),
                    (var1, var2)
                )
    
    def _add_faculty_conflict_constraints(self):
        """Ensure no faculty has overlapping classes."""
        var_names = list(self.variables.keys())
        
        for i in range(len(var_names)):
            for j in range(i + 1, len(var_names)):
                var1, var2 = var_names[i], var_names[j]
                
                def no_faculty_conflict(assignment1, assignment2):
                    faculty1, room1, timeslot1 = assignment1
                    faculty2, room2, timeslot2 = assignment2
                    
                    # If different faculty or non-overlapping times, no conflict
                    if faculty1 != faculty2:
                        return True
                    
                    return not timeslot1.overlaps_with(timeslot2)
                
                self.problem.addConstraint(
                    FunctionConstraint(no_faculty_conflict),
                    (var1, var2)
                )
    
    def _add_student_conflict_constraints(self):
        """Ensure no student has overlapping classes."""
        var_names = list(self.variables.keys())
        
        for i in range(len(var_names)):
            for j in range(i + 1, len(var_names)):
                var1, var2 = var_names[i], var_names[j]
                
                course1 = self.variables[var1]['course']
                course2 = self.variables[var2]['course']
                
                # Check if courses share students
                common_students = course1.enrolled_students & course2.enrolled_students
                
                if not common_students:
                    continue
                
                def no_student_conflict(assignment1, assignment2):
                    faculty1, room1, timeslot1 = assignment1
                    faculty2, room2, timeslot2 = assignment2
                    
                    return not timeslot1.overlaps_with(timeslot2)
                
                self.problem.addConstraint(
                    FunctionConstraint(no_student_conflict),
                    (var1, var2)
                )
    
    def solve(self, max_solutions: int = 1) -> List[Timetable]:
        """
        Solve the CSP and return valid timetables.
        
        Args:
            max_solutions: Maximum number of solutions to find
            
        Returns:
            List of valid timetables
        """
        solutions = []
        
        # Get CSP solutions
        csp_solutions = self.problem.getSolutions()
        
        if not csp_solutions:
            return []
        
        # Convert solutions to timetables
        for csp_solution in csp_solutions[:max_solutions]:
            timetable = self._solution_to_timetable(csp_solution)
            solutions.append(timetable)
        
        return solutions
    
    def _solution_to_timetable(self, solution: Dict[str, Tuple]) -> Timetable:
        """Convert CSP solution to timetable."""
        timetable = Timetable()
        
        for var_name, assignment in solution.items():
            faculty, room, timeslot = assignment
            course_info = self.variables[var_name]
            course = course_info['course']
            
            # Create schedule slot
            slot = ScheduleSlot(
                course=course,
                faculty=faculty,
                room=room,
                time_slot=timeslot,
                students=course.enrolled_students
            )
            
            timetable.add_slot(slot)
        
        return timetable
    
    def get_partial_solution(self) -> Optional[Timetable]:
        """
        Get a partial solution even if complete solution not found.
        Useful for large problem instances.
        """
        # Try to get at least one solution
        solution = self.problem.getSolution()
        
        if solution:
            return self._solution_to_timetable(solution)
        
        return None
