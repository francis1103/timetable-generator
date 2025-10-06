"""NSGA-II based multi-objective optimization for timetable generation."""

import random
import numpy as np
from typing import List, Tuple, Set, Dict, Any, Callable, TYPE_CHECKING
from deap import base, creator, tools, algorithms
from dataclasses import dataclass
import copy

from src.models.entities import Course, Faculty, Room, TimeSlot, Student
from src.models.schedule import Timetable, ScheduleSlot
from src.constraints.validators import ConstraintValidator
from src.constraints.hard_constraints import *
from src.constraints.soft_constraints import *

# Initialize DEAP creator types at module level
if not hasattr(creator, "FitnessMulti"):
    creator.create("FitnessMulti", base.Fitness, weights=(-1.0, -1.0, 1.0))

if not hasattr(creator, "Individual"):
    creator.create("Individual", list, fitness=creator.FitnessMulti)


@dataclass
class OptimizationConfig:
    """Configuration for NSGA-II optimization."""
    population_size: int = 100
    num_generations: int = 50
    crossover_probability: float = 0.7
    mutation_probability: float = 0.2
    tournament_size: int = 3
    elite_size: int = 10
    max_stagnant_generations: int = 15
    

class NSGA2Optimizer:
    """
    Multi-objective genetic algorithm optimizer using NSGA-II.
    Optimizes timetable generation with multiple competing objectives.
    """
    
    def __init__(self, 
                 courses: List[Course],
                 faculty: List[Faculty],
                 rooms: List[Room],
                 time_slots: List[TimeSlot],
                 students: List[Student],
                 config: OptimizationConfig = None):
        """
        Initialize the NSGA-II optimizer.
        
        Args:
            courses: List of courses to schedule
            faculty: List of available faculty
            rooms: List of available rooms
            time_slots: List of available time slots
            students: List of students
            config: Optimization configuration
        """
        self.courses = courses
        self.faculty_list = faculty
        self.rooms = rooms
        self.time_slots = time_slots
        self.students = students
        self.config = config or OptimizationConfig()
        
        # Create constraint validators
        self.hard_constraints = [
            NoRoomOverlapConstraint(),
            NoFacultyOverlapConstraint(),
            NoStudentOverlapConstraint(),
            RoomCapacityConstraint(),
            FacultyAvailabilityConstraint(),
            StudentAvailabilityConstraint(),
            MaxSubjectsPerDayConstraint(),
        ]
        
        self.soft_constraints = [
            FacultyWorkloadBalanceConstraint(weight=2.0),
            MinimizeTravelTimeConstraint(weight=1.5),
            TimePreferenceConstraint(weight=1.0),
            SubjectSpacingConstraint(weight=1.0),
            ConsecutiveClassLimitConstraint(max_consecutive=3, weight=1.5),
        ]
        
        # Initialize DEAP framework
        self._setup_deap()
        
        # Statistics
        self.generation_stats = []
        self.best_solutions = []
    
    def _setup_deap(self):
        """Set up DEAP genetic algorithm framework."""
        # Creator types are initialized at module level
        self.toolbox = base.Toolbox()
        
        # Register genetic operators
        self.toolbox.register("individual", self._create_individual)
        self.toolbox.register("population", tools.initRepeat, list, self.toolbox.individual)
        self.toolbox.register("evaluate", self._evaluate_timetable)
        self.toolbox.register("mate", self._crossover)
        self.toolbox.register("mutate", self._mutate)
        self.toolbox.register("select", tools.selNSGA2)
    
    def _create_individual(self):
        """
        Create a random timetable individual.
        
        Each gene represents a schedule slot assignment:
        [course_idx, faculty_idx, room_idx, timeslot_idx, students]
        """
        individual = []
        
        for course in self.courses:
            # Determine sessions per week
            sessions = course.sessions_per_week
            
            for _ in range(sessions):
                # Randomly assign faculty
                eligible_faculty = [
                    f for f in self.faculty_list
                    if course.department == f.department or
                    any(spec in course.name.lower() for spec in f.specializations)
                ]
                
                if not eligible_faculty:
                    eligible_faculty = self.faculty_list
                
                faculty_idx = self.faculty_list.index(random.choice(eligible_faculty))
                
                # Randomly assign room
                eligible_rooms = [
                    r for r in self.rooms
                    if r.room_type == course.required_room_type and
                    r.capacity >= course.get_enrolled_count()
                ]
                
                if not eligible_rooms:
                    eligible_rooms = self.rooms
                
                room_idx = self.rooms.index(random.choice(eligible_rooms))
                
                # Randomly assign time slot
                timeslot_idx = random.randint(0, len(self.time_slots) - 1)
                
                # Get enrolled students
                student_ids = [s.student_id for s in course.enrolled_students]
                
                gene = {
                    'course_idx': self.courses.index(course),
                    'faculty_idx': faculty_idx,
                    'room_idx': room_idx,
                    'timeslot_idx': timeslot_idx,
                    'student_ids': student_ids
                }
                
                individual.append(gene)
        
        return creator.Individual(individual)
    
    def _decode_individual(self, individual: List[Dict]) -> Timetable:
        """Convert individual (genotype) to timetable (phenotype)."""
        timetable = Timetable()
        
        for gene in individual:
            course = self.courses[gene['course_idx']]
            faculty = self.faculty_list[gene['faculty_idx']]
            room = self.rooms[gene['room_idx']]
            time_slot = self.time_slots[gene['timeslot_idx']]
            
            # Get student objects
            students = set(
                s for s in self.students
                if s.student_id in gene['student_ids']
            )
            
            slot = ScheduleSlot(
                course=course,
                faculty=faculty,
                room=room,
                time_slot=time_slot,
                students=students
            )
            
            timetable.add_slot(slot)
        
        return timetable
    
    def _evaluate_timetable(self, individual: List[Dict]) -> Tuple[float, float, float]:
        """
        Evaluate fitness of a timetable.
        
        Returns:
            (hard_violations, soft_violations, preference_satisfaction)
        """
        timetable = self._decode_individual(individual)
        
        # Evaluate hard constraints
        hard_violation_count = 0
        for constraint in self.hard_constraints:
            if not constraint.enabled:
                continue
            is_valid, violations = constraint.validate(timetable)
            hard_violation_count += len(violations)
        
        # Evaluate soft constraints
        soft_penalty = 0.0
        for constraint in self.soft_constraints:
            if not constraint.enabled:
                continue
            is_valid, violations = constraint.validate(timetable)
            soft_penalty += constraint.get_penalty(violations)
        
        # Calculate preference satisfaction (higher is better)
        preference_score = 0.0
        for constraint in self.soft_constraints:
            if not constraint.enabled:
                continue
            score = constraint.calculate_satisfaction_score(timetable)
            preference_score += score * constraint.weight
        
        return (hard_violation_count, soft_penalty, preference_score)
    
    def _crossover(self, ind1: List[Dict], ind2: List[Dict]) -> Tuple[List[Dict], List[Dict]]:
        """
        Perform crossover between two individuals.
        Uses uniform crossover with gene-level swapping.
        """
        if len(ind1) != len(ind2):
            return ind1, ind2
        
        child1 = copy.deepcopy(ind1)
        child2 = copy.deepcopy(ind2)
        
        # Uniform crossover
        for i in range(len(ind1)):
            if random.random() < 0.5:
                child1[i], child2[i] = child2[i], child1[i]
        
        return creator.Individual(child1), creator.Individual(child2)
    
    def _mutate(self, individual: List[Dict]) -> Tuple[List[Dict]]:
        """
        Mutate an individual.
        Randomly modifies faculty, room, or timeslot assignments.
        """
        mutated = copy.deepcopy(individual)
        
        # Mutate random genes
        for i in range(len(mutated)):
            if random.random() < self.config.mutation_probability:
                mutation_type = random.choice(['faculty', 'room', 'timeslot'])
                
                if mutation_type == 'faculty':
                    mutated[i]['faculty_idx'] = random.randint(0, len(self.faculty_list) - 1)
                elif mutation_type == 'room':
                    mutated[i]['room_idx'] = random.randint(0, len(self.rooms) - 1)
                else:  # timeslot
                    mutated[i]['timeslot_idx'] = random.randint(0, len(self.time_slots) - 1)
        
        return (creator.Individual(mutated),)
    
    def optimize(self, verbose: bool = True) -> Tuple[Timetable, Dict[str, Any]]:
        """
        Run the NSGA-II optimization algorithm.
        
        Args:
            verbose: Print progress information
            
        Returns:
            (best_timetable, optimization_stats)
        """
        # Create initial population
        population = self.toolbox.population(n=self.config.population_size)
        
        # Evaluate initial population
        fitnesses = list(map(self.toolbox.evaluate, population))
        for ind, fit in zip(population, fitnesses):
            ind.fitness.values = fit
        
        # Statistics
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("min", np.min, axis=0)
        stats.register("avg", np.mean, axis=0)
        stats.register("max", np.max, axis=0)
        
        logbook = tools.Logbook()
        logbook.header = "gen", "evals", "min", "avg", "max"
        
        # Evolution loop
        best_fitness = float('inf')
        stagnant_count = 0
        
        for gen in range(self.config.num_generations):
            # Select next generation
            offspring = self.toolbox.select(population, len(population))
            offspring = list(map(self.toolbox.clone, offspring))
            
            # Apply crossover
            for child1, child2 in zip(offspring[::2], offspring[1::2]):
                if random.random() < self.config.crossover_probability:
                    self.toolbox.mate(child1, child2)
                    del child1.fitness.values
                    del child2.fitness.values
            
            # Apply mutation
            for mutant in offspring:
                if random.random() < self.config.mutation_probability:
                    self.toolbox.mutate(mutant)
                    del mutant.fitness.values
            
            # Evaluate individuals with invalid fitness
            invalid_ind = [ind for ind in offspring if not ind.fitness.valid]
            fitnesses = map(self.toolbox.evaluate, invalid_ind)
            for ind, fit in zip(invalid_ind, fitnesses):
                ind.fitness.values = fit
            
            # Replace population
            population[:] = offspring
            
            # Record statistics
            record = stats.compile(population)
            logbook.record(gen=gen, evals=len(invalid_ind), **record)
            
            if verbose:
                print(f"Gen {gen}: Hard={record['min'][0]:.0f}, Soft={record['min'][1]:.2f}, Pref={record['max'][2]:.2f}")
            
            # Check for improvement
            current_best = record['min'][0]
            if current_best < best_fitness:
                best_fitness = current_best
                stagnant_count = 0
            else:
                stagnant_count += 1
            
            # Early stopping
            if best_fitness == 0 or stagnant_count >= self.config.max_stagnant_generations:
                if verbose:
                    print(f"Stopping early at generation {gen}")
                break
        
        # Get best individual from final population
        pareto_front = tools.sortNondominated(population, len(population), first_front_only=True)[0]
        
        # Select individual with fewest hard violations, then best soft score
        best_individual = min(pareto_front, key=lambda ind: (ind.fitness.values[0], ind.fitness.values[1]))
        
        best_timetable = self._decode_individual(best_individual)
        
        # Compile statistics
        optimization_stats = {
            'generations': gen + 1,
            'final_population_size': len(population),
            'best_fitness': best_individual.fitness.values,
            'pareto_front_size': len(pareto_front),
            'logbook': logbook,
        }
        
        # Store fitness scores in timetable
        best_timetable.fitness_scores = {
            'hard_violations': best_individual.fitness.values[0],
            'soft_penalty': best_individual.fitness.values[1],
            'preference_score': best_individual.fitness.values[2],
        }
        
        return best_timetable, optimization_stats
    
    def get_pareto_front(self, population: List) -> List[Timetable]:
        """Extract Pareto-optimal solutions from population."""
        pareto_front = tools.sortNondominated(population, len(population), first_front_only=True)[0]
        return [self._decode_individual(ind) for ind in pareto_front]
