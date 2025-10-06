"""Integer Linear Programming solver for conflict resolution."""

from typing import List, Dict, Set, Optional, Tuple
import pulp as pl

from src.models.entities import Course, Faculty, Room, TimeSlot, Student
from src.models.schedule import Timetable, ScheduleSlot


class ILPSolver:
    """
    Integer Linear Programming solver for timetable optimization.
    Used for conflict resolution and resource allocation.
    """
    
    def __init__(self,
                 courses: List[Course],
                 faculty: List[Faculty],
                 rooms: List[Room],
                 time_slots: List[TimeSlot],
                 students: List[Student]):
        """
        Initialize ILP solver.
        
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
        
        # Create ILP problem
        self.problem = pl.LpProblem("Timetable_Optimization", pl.LpMinimize)
        self.variables = {}
        
    def build_model(self, existing_timetable: Optional[Timetable] = None):
        """
        Build the ILP model for timetable optimization.
        
        Args:
            existing_timetable: Existing timetable to improve (optional)
        """
        # Decision variables: x[c,s,f,r,t] = 1 if course c session s is assigned
        # to faculty f, room r, timeslot t
        
        for course in self.courses:
            for session in range(course.sessions_per_week):
                for faculty in self.faculty_list:
                    for room in self.rooms:
                        for timeslot in self.time_slots:
                            var_name = f"x_{course.course_id}_{session}_{faculty.faculty_id}_{room.room_id}_{timeslot.slot_id}"
                            
                            # Binary variable
                            self.variables[var_name] = pl.LpVariable(
                                var_name,
                                cat=pl.LpBinary
                            )
        
        self._add_constraints()
        self._add_objective(existing_timetable)
    
    def _add_constraints(self):
        """Add all ILP constraints."""
        # Each course session must be assigned exactly once
        for course in self.courses:
            for session in range(course.sessions_per_week):
                session_vars = [
                    var for name, var in self.variables.items()
                    if name.startswith(f"x_{course.course_id}_{session}_")
                ]
                
                if session_vars:
                    self.problem += (
                        pl.lpSum(session_vars) == 1,
                        f"assign_course_{course.course_id}_session_{session}"
                    )
        
        # No room conflicts
        for room in self.rooms:
            for timeslot in self.time_slots:
                room_slot_vars = [
                    var for name, var in self.variables.items()
                    if f"_{room.room_id}_{timeslot.slot_id}" in name
                ]
                
                if room_slot_vars:
                    self.problem += (
                        pl.lpSum(room_slot_vars) <= 1,
                        f"room_{room.room_id}_slot_{timeslot.slot_id}"
                    )
        
        # No faculty conflicts
        for faculty in self.faculty_list:
            for timeslot in self.time_slots:
                faculty_slot_vars = [
                    var for name, var in self.variables.items()
                    if f"_{faculty.faculty_id}_" in name and f"_{timeslot.slot_id}" in name
                ]
                
                if faculty_slot_vars:
                    self.problem += (
                        pl.lpSum(faculty_slot_vars) <= 1,
                        f"faculty_{faculty.faculty_id}_slot_{timeslot.slot_id}"
                    )
        
        # Room capacity constraints
        for course in self.courses:
            student_count = course.get_enrolled_count()
            
            for session in range(course.sessions_per_week):
                for room in self.rooms:
                    if room.capacity < student_count:
                        # Cannot use this room
                        invalid_vars = [
                            var for name, var in self.variables.items()
                            if name.startswith(f"x_{course.course_id}_{session}_") and
                            f"_{room.room_id}_" in name
                        ]
                        
                        for var in invalid_vars:
                            self.problem += (
                                var == 0,
                                f"capacity_{course.course_id}_{session}_{room.room_id}"
                            )
    
    def _add_objective(self, existing_timetable: Optional[Timetable] = None):
        """
        Add objective function to minimize.
        
        Minimizes:
        - Number of changes from existing timetable (if provided)
        - Soft constraint violations
        """
        objective_terms = []
        
        # If existing timetable provided, minimize changes
        if existing_timetable:
            for slot in existing_timetable.schedule_slots:
                # Find corresponding variable
                var_name = None
                for name in self.variables.keys():
                    if (f"x_{slot.course.course_id}_" in name and
                        f"_{slot.faculty.faculty_id}_" in name and
                        f"_{slot.room.room_id}_" in name and
                        f"_{slot.time_slot.slot_id}" in name):
                        var_name = name
                        break
                
                if var_name:
                    # Penalize changes (prefer keeping existing assignments)
                    objective_terms.append(-10 * self.variables[var_name])
        
        # Add soft constraint penalties
        # (Simplified - in full implementation, add all soft constraints)
        
        # Prefer faculty teaching in their preferred times
        for faculty in self.faculty_list:
            for timeslot in faculty.preferred_slots:
                pref_vars = [
                    var for name, var in self.variables.items()
                    if f"_{faculty.faculty_id}_" in name and f"_{timeslot.slot_id}" in name
                ]
                
                for var in pref_vars:
                    objective_terms.append(-5 * var)  # Reward for using preferred slot
        
        # Set objective
        if objective_terms:
            self.problem += pl.lpSum(objective_terms)
    
    def solve(self, time_limit: int = 300) -> Optional[Timetable]:
        """
        Solve the ILP problem.
        
        Args:
            time_limit: Maximum time in seconds
            
        Returns:
            Optimized timetable or None if infeasible
        """
        # Solve using CBC solver
        solver = pl.PULP_CBC_CMD(timeLimit=time_limit, msg=True)
        status = self.problem.solve(solver)
        
        if status != pl.LpStatusOptimal and status != pl.LpStatusFeasible:
            return None
        
        # Extract solution
        return self._extract_solution()
    
    def _extract_solution(self) -> Timetable:
        """Extract timetable from ILP solution."""
        timetable = Timetable()
        
        for var_name, var in self.variables.items():
            if var.varValue and var.varValue > 0.5:  # Variable is set to 1
                # Parse variable name
                parts = var_name.split('_')
                # x_course_session_faculty_room_timeslot
                
                course_id = parts[1]
                session = int(parts[2])
                faculty_id = parts[3]
                room_id = parts[4]
                # Rest is timeslot_id
                timeslot_id = '_'.join(parts[5:])
                
                # Find entities
                course = next((c for c in self.courses if c.course_id == course_id), None)
                faculty = next((f for f in self.faculty_list if f.faculty_id == faculty_id), None)
                room = next((r for r in self.rooms if r.room_id == room_id), None)
                timeslot = next((t for t in self.time_slots if t.slot_id == timeslot_id), None)
                
                if course and faculty and room and timeslot:
                    slot = ScheduleSlot(
                        course=course,
                        faculty=faculty,
                        room=room,
                        time_slot=timeslot,
                        students=course.enrolled_students
                    )
                    
                    timetable.add_slot(slot)
        
        return timetable
    
    def resolve_conflicts(self, timetable: Timetable) -> Timetable:
        """
        Resolve conflicts in an existing timetable.
        
        Args:
            timetable: Timetable with conflicts
            
        Returns:
            Conflict-free timetable
        """
        # Build model with existing timetable as base
        self.build_model(existing_timetable=timetable)
        
        # Solve
        return self.solve()
