"""Main timetable scheduler orchestrating all components."""

from typing import List, Dict, Optional, Any
from pathlib import Path
import json

from src.models.entities import Course, Faculty, Room, TimeSlot, Student
from src.models.schedule import Schedule, Timetable
from src.optimization.nsga2_optimizer import NSGA2Optimizer, OptimizationConfig
from src.optimization.csp_solver import CSPSolver
from src.optimization.ilp_solver import ILPSolver
from src.parsers.data_parser import DataParser
from src.exporters.timetable_exporter import TimetableExporter


class TimetableScheduler:
    """
    Main scheduler class that orchestrates the entire timetable generation process.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the timetable scheduler.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path) if config_path else {}
        
        # Data containers
        self.courses: List[Course] = []
        self.faculty: List[Faculty] = []
        self.rooms: List[Room] = []
        self.time_slots: List[TimeSlot] = []
        self.students: List[Student] = []
        
        # Schedule manager
        self.schedule = Schedule()
        
        # Parsers and exporters
        self.parser = DataParser()
        self.exporter = TimetableExporter()
        
        # Optimization configuration
        self.optimization_config = OptimizationConfig(
            population_size=self.config.get('population_size', 100),
            num_generations=self.config.get('num_generations', 50),
            crossover_probability=self.config.get('crossover_probability', 0.7),
            mutation_probability=self.config.get('mutation_probability', 0.2),
        )
    
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        with open(config_path, 'r') as f:
            if config_path.endswith('.json'):
                return json.load(f)
            elif config_path.endswith('.yaml') or config_path.endswith('.yml'):
                import yaml
                return yaml.safe_load(f)
        return {}
    
    def load_data(self, data_source: str, format: str = 'auto'):
        """
        Load scheduling data from various sources.
        
        Args:
            data_source: Path to data file or directory
            format: Data format ('csv', 'excel', 'json', 'auto')
        """
        data = self.parser.parse(data_source, format)
        
        self.courses = data.get('courses', [])
        self.faculty = data.get('faculty', [])
        self.rooms = data.get('rooms', [])
        self.time_slots = data.get('time_slots', [])
        self.students = data.get('students', [])
        
        # Update schedule
        self.schedule.all_courses = set(self.courses)
        self.schedule.all_faculty = set(self.faculty)
        self.schedule.all_rooms = set(self.rooms)
        self.schedule.all_time_slots = set(self.time_slots)
        self.schedule.all_students = set(self.students)
    
    def add_natural_language_rule(self, rule: str):
        """
        Add a scheduling rule in natural language.
        
        Args:
            rule: Natural language rule (e.g., "No CS classes after 3pm on Fridays")
        """
        parsed_constraints = self.parser.parse_natural_language_rule(rule)
        # Apply parsed constraints to the system
        # Implementation depends on NLP parser
    
    def generate_optimal_schedule(self, 
                                 method: str = 'nsga2',
                                 verbose: bool = True) -> Timetable:
        """
        Generate optimal timetable using specified method.
        
        Args:
            method: Optimization method ('nsga2', 'csp', 'ilp', 'hybrid')
            verbose: Print progress information
            
        Returns:
            Optimized timetable
        """
        if method == 'nsga2':
            return self._generate_with_nsga2(verbose)
        elif method == 'csp':
            return self._generate_with_csp(verbose)
        elif method == 'ilp':
            return self._generate_with_ilp(verbose)
        elif method == 'hybrid':
            return self._generate_hybrid(verbose)
        else:
            raise ValueError(f"Unknown method: {method}")
    
    def _generate_with_nsga2(self, verbose: bool = True) -> Timetable:
        """Generate timetable using NSGA-II genetic algorithm."""
        if verbose:
            print("Generating timetable using NSGA-II optimization...")
        
        optimizer = NSGA2Optimizer(
            courses=self.courses,
            faculty=self.faculty,
            rooms=self.rooms,
            time_slots=self.time_slots,
            students=self.students,
            config=self.optimization_config
        )
        
        timetable, stats = optimizer.optimize(verbose=verbose)
        
        if verbose:
            print(f"\nOptimization complete!")
            print(f"Generations: {stats['generations']}")
            print(f"Hard violations: {timetable.fitness_scores['hard_violations']}")
            print(f"Soft penalty: {timetable.fitness_scores['soft_penalty']:.2f}")
            print(f"Preference score: {timetable.fitness_scores['preference_score']:.2f}")
        
        self.schedule.set_current_timetable(timetable)
        return timetable
    
    def _generate_with_csp(self, verbose: bool = True) -> Timetable:
        """Generate timetable using CSP solver."""
        if verbose:
            print("Generating timetable using CSP solver...")
        
        solver = CSPSolver(
            courses=self.courses,
            faculty=self.faculty,
            rooms=self.rooms,
            time_slots=self.time_slots,
            students=self.students
        )
        
        solutions = solver.solve(max_solutions=1)
        
        if solutions:
            timetable = solutions[0]
            if verbose:
                print(f"CSP solution found with {timetable.get_total_slots()} slots")
        else:
            if verbose:
                print("No complete CSP solution found, trying partial solution...")
            timetable = solver.get_partial_solution()
        
        if timetable:
            self.schedule.set_current_timetable(timetable)
        
        return timetable
    
    def _generate_with_ilp(self, verbose: bool = True) -> Timetable:
        """Generate timetable using ILP solver."""
        if verbose:
            print("Generating timetable using ILP solver...")
        
        solver = ILPSolver(
            courses=self.courses,
            faculty=self.faculty,
            rooms=self.rooms,
            time_slots=self.time_slots,
            students=self.students
        )
        
        solver.build_model()
        timetable = solver.solve(time_limit=300)
        
        if timetable:
            if verbose:
                print(f"ILP solution found with {timetable.get_total_slots()} slots")
            self.schedule.set_current_timetable(timetable)
        
        return timetable
    
    def _generate_hybrid(self, verbose: bool = True) -> Timetable:
        """
        Generate timetable using hybrid approach.
        1. CSP for initial feasible solution
        2. NSGA-II for optimization
        3. ILP for final conflict resolution
        """
        if verbose:
            print("Generating timetable using hybrid approach...")
        
        # Step 1: CSP for feasibility
        if verbose:
            print("\nStep 1: Finding feasible solution with CSP...")
        csp_solver = CSPSolver(
            courses=self.courses,
            faculty=self.faculty,
            rooms=self.rooms,
            time_slots=self.time_slots,
            students=self.students
        )
        
        initial_solution = csp_solver.get_partial_solution()
        
        # Step 2: Optimize with NSGA-II
        if verbose:
            print("\nStep 2: Optimizing with NSGA-II...")
        timetable = self._generate_with_nsga2(verbose=False)
        
        # Step 3: Resolve any remaining conflicts with ILP
        if not timetable.is_valid():
            if verbose:
                print("\nStep 3: Resolving conflicts with ILP...")
            ilp_solver = ILPSolver(
                courses=self.courses,
                faculty=self.faculty,
                rooms=self.rooms,
                time_slots=self.time_slots,
                students=self.students
            )
            timetable = ilp_solver.resolve_conflicts(timetable)
        
        if verbose:
            print("\nHybrid optimization complete!")
            conflicts = timetable.detect_conflicts()
            print(f"Final conflicts: {len(conflicts)}")
        
        self.schedule.set_current_timetable(timetable)
        return timetable
    
    def resolve_conflicts(self, timetable: Optional[Timetable] = None) -> Timetable:
        """
        Resolve conflicts in the current or provided timetable.
        
        Args:
            timetable: Timetable to fix (uses current if not provided)
            
        Returns:
            Conflict-free timetable
        """
        target = timetable or self.schedule.current_timetable
        
        if not target:
            raise ValueError("No timetable to resolve")
        
        ilp_solver = ILPSolver(
            courses=self.courses,
            faculty=self.faculty,
            rooms=self.rooms,
            time_slots=self.time_slots,
            students=self.students
        )
        
        resolved = ilp_solver.resolve_conflicts(target)
        
        if resolved:
            self.schedule.set_current_timetable(resolved)
        
        return resolved
    
    def dynamic_reschedule(self, 
                          course: Course, 
                          new_faculty: Optional[Faculty] = None,
                          new_time: Optional[TimeSlot] = None) -> bool:
        """
        Dynamically reschedule a course without creating conflicts.
        
        Args:
            course: Course to reschedule
            new_faculty: New faculty (if changing)
            new_time: New time slot (if changing)
            
        Returns:
            True if successful
        """
        if not self.schedule.current_timetable:
            return False
        
        # Find slots for this course
        course_slots = [
            slot for slot in self.schedule.current_timetable.schedule_slots
            if slot.course == course
        ]
        
        # Try rescheduling with ILP
        # (Simplified - full implementation would use ILP with additional constraints)
        
        return True
    
    def export(self, 
               output_path: str, 
               format: str = 'pdf',
               timetable: Optional[Timetable] = None):
        """
        Export timetable to file.
        
        Args:
            output_path: Output file path
            format: Export format ('pdf', 'excel', 'json', 'ical', 'html')
            timetable: Timetable to export (uses current if not provided)
        """
        target = timetable or self.schedule.current_timetable
        
        if not target:
            raise ValueError("No timetable to export")
        
        self.exporter.export(target, output_path, format)
    
    def get_conflict_report(self, timetable: Optional[Timetable] = None) -> Dict[str, Any]:
        """
        Generate detailed conflict analysis report.
        
        Args:
            timetable: Timetable to analyze (uses current if not provided)
            
        Returns:
            Conflict report
        """
        target = timetable or self.schedule.current_timetable
        
        if not target:
            return {}
        
        conflicts = target.detect_conflicts()
        
        report = {
            'total_conflicts': len(conflicts),
            'is_valid': target.is_valid(),
            'total_slots': target.get_total_slots(),
            'conflicts_by_type': {},
            'detailed_conflicts': []
        }
        
        for slot1, slot2, reasons in conflicts:
            report['detailed_conflicts'].append({
                'slot1': {
                    'course': slot1.course.name,
                    'faculty': slot1.faculty.name,
                    'room': slot1.room.name,
                    'time': f"{slot1.time_slot.day.name} {slot1.time_slot.start_time}"
                },
                'slot2': {
                    'course': slot2.course.name,
                    'faculty': slot2.faculty.name,
                    'room': slot2.room.name,
                    'time': f"{slot2.time_slot.day.name} {slot2.time_slot.start_time}"
                },
                'reasons': reasons
            })
            
            for reason in reasons:
                report['conflicts_by_type'][reason] = \
                    report['conflicts_by_type'].get(reason, 0) + 1
        
        return report
    
    def get_recommendations(self) -> List[str]:
        """Get AI-powered scheduling recommendations."""
        recommendations = []
        
        if not self.schedule.current_timetable:
            return ["Generate a timetable first"]
        
        # Analyze current timetable
        conflicts = self.schedule.current_timetable.detect_conflicts()
        stats = self.schedule.current_timetable.get_utilization_stats()
        
        if conflicts:
            recommendations.append(
                f"Found {len(conflicts)} conflicts - run resolve_conflicts() to fix"
            )
        
        if stats.get('max_faculty_hours', 0) > 20:
            recommendations.append(
                "Some faculty are overloaded - consider redistributing workload"
            )
        
        if stats.get('min_faculty_hours', 0) < 10:
            recommendations.append(
                "Some faculty are underutilized - consider assigning more courses"
            )
        
        return recommendations
