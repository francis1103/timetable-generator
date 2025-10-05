# AI-Powered University Timetable Scheduler - User Guide

## Table of Contents
1. [Introduction](#introduction)
2. [Installation](#installation)
3. [Quick Start](#quick-start)
4. [Data Preparation](#data-preparation)
5. [Generating Timetables](#generating-timetables)
6. [API Usage](#api-usage)
7. [Advanced Features](#advanced-features)
8. [Troubleshooting](#troubleshooting)

## Introduction

The AI-Powered Timetable Scheduler is an intelligent system that generates optimal, clash-free schedules for educational institutions using advanced optimization algorithms and machine learning.

### Key Features

- **Multi-Objective Optimization**: Uses NSGA-II genetic algorithm to balance multiple competing objectives
- **Hard Constraint Enforcement**: Ensures no room/faculty/student overlaps
- **Soft Constraint Optimization**: Balances workload, preferences, and spacing
- **Natural Language Rules**: Accept rules like "No classes after 3 PM on Fridays"
- **Multiple Input Formats**: CSV, Excel, JSON, Google Sheets
- **Multiple Output Formats**: PDF, Excel, JSON, iCal, HTML
- **Real-Time API**: REST API with WebSocket support for live updates
- **Conflict Resolution**: Automatic ILP-based conflict resolution
- **AI Recommendations**: Intelligent suggestions for improvement

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)

### Steps

1. Clone or download the repository:
```bash
cd timetableshudler
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv

# On Windows
venv\Scripts\activate

# On Mac/Linux
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Download spaCy language model:
```bash
python -m spacy download en_core_web_sm
```

## Quick Start

### Using the Example Script

The easiest way to get started is to run the example script:

```bash
python example.py
```

This will:
- Create sample data
- Generate an optimal timetable
- Resolve any conflicts
- Export results to multiple formats

### Using CSV Data

1. Prepare your data in CSV format (see [Data Preparation](#data-preparation))

2. Create a Python script:

```python
from src.optimization.scheduler import TimetableScheduler

# Initialize scheduler
scheduler = TimetableScheduler()

# Load data
scheduler.load_data('data', format='csv')

# Generate timetable
timetable = scheduler.generate_optimal_schedule(method='nsga2')

# Export results
scheduler.export('output/timetable.pdf', format='pdf')
```

3. Run the script:
```bash
python your_script.py
```

## Data Preparation

### CSV Format

Create four CSV files in your data directory:

#### courses.csv
```csv
course_id,name,code,department,credits,duration_minutes,sessions_per_week,room_type,max_students
CS101,Data Structures,CS101,Computer Science,4,60,3,lecture_hall,50
```

Required columns:
- `course_id`: Unique identifier
- `name`: Course name
- `code`: Course code
- `department`: Department name

Optional columns:
- `credits`, `duration_minutes`, `sessions_per_week`, `room_type`, `max_students`, `is_lab`

#### faculty.csv
```csv
faculty_id,name,email,department,specializations,max_hours_per_week
F001,Dr. Alice Smith,alice@uni.edu,Computer Science,algorithms;data structures,18
```

Required columns:
- `faculty_id`: Unique identifier
- `name`: Faculty name

Optional columns:
- `email`, `department`, `specializations` (semicolon-separated), `max_hours_per_week`, `max_consecutive_classes`

#### rooms.csv
```csv
room_id,name,capacity,room_type,building,floor
R101,Lecture Hall A,60,lecture_hall,A,1
```

Required columns:
- `room_id`: Unique identifier
- `name`: Room name
- `capacity`: Maximum capacity
- `room_type`: One of: lecture_hall, laboratory, seminar_room, auditorium, computer_lab

Optional columns:
- `building`, `floor`, `facilities` (semicolon-separated)

#### students.csv
```csv
student_id,name,email,department,year,semester,enrolled_courses
S001,John Doe,john@uni.edu,Computer Science,2,3,CS101;CS102;MATH201
```

Required columns:
- `student_id`: Unique identifier
- `name`: Student name

Optional columns:
- `email`, `department`, `year`, `semester`, `enrolled_courses` (semicolon-separated), `max_subjects_per_day`

### Excel Format

Create an Excel file with sheets named: `courses`, `faculty`, `rooms`, `students`

Each sheet should have the same columns as the CSV format.

### JSON Format

```json
{
  "courses": [...],
  "faculty": [...],
  "rooms": [...],
  "students": [...]
}
```

## Generating Timetables

### Optimization Methods

The system supports four optimization methods:

#### 1. NSGA-II (Recommended)
Multi-objective genetic algorithm. Best for complex scenarios.

```python
timetable = scheduler.generate_optimal_schedule(method='nsga2')
```

Parameters:
- `population_size`: Number of individuals (default: 100)
- `num_generations`: Evolution iterations (default: 50)
- `crossover_probability`: Crossover rate (default: 0.7)
- `mutation_probability`: Mutation rate (default: 0.2)

#### 2. CSP (Constraint Satisfaction)
Finds feasible solutions quickly. Good for simple scenarios.

```python
timetable = scheduler.generate_optimal_schedule(method='csp')
```

#### 3. ILP (Integer Linear Programming)
Optimal solutions for specific objective functions.

```python
timetable = scheduler.generate_optimal_schedule(method='ilp')
```

#### 4. Hybrid (Best Quality)
Combines all three methods for highest quality results.

```python
timetable = scheduler.generate_optimal_schedule(method='hybrid')
```

### Adding Natural Language Rules

```python
scheduler.add_natural_language_rule(
    "No classes for Computer Science students after 3 PM on Fridays"
)

scheduler.add_natural_language_rule(
    "Dr. Alice Smith prefers morning slots"
)

scheduler.add_natural_language_rule(
    "Max 2 consecutive classes for all faculty"
)
```

### Conflict Resolution

If the generated timetable has conflicts:

```python
# Check for conflicts
report = scheduler.get_conflict_report()
print(f"Conflicts: {report['total_conflicts']}")

# Resolve conflicts
resolved = scheduler.resolve_conflicts()
```

## API Usage

### Starting the API Server

```bash
# Development mode
uvicorn src.api.main:app --reload

# Production mode
uvicorn src.api.main:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Load Data
```bash
POST /api/load-data
{
  "data_source": "data",
  "format": "csv"
}
```

#### Generate Schedule
```bash
POST /api/generate
{
  "method": "nsga2",
  "population_size": 100,
  "num_generations": 50,
  "verbose": true
}
```

#### Get Current Timetable
```bash
GET /api/timetable
```

#### Get Conflicts
```bash
GET /api/conflicts
```

#### Resolve Conflicts
```bash
POST /api/resolve-conflicts
```

#### Get Recommendations
```bash
GET /api/recommendations
```

#### Export Timetable
```bash
POST /api/export
{
  "output_path": "output/timetable.pdf",
  "format": "pdf"
}
```

### WebSocket Connection

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Update:', data);
};
```

## Advanced Features

### Custom Constraint Weights

Modify `config.yaml` to adjust constraint weights:

```yaml
constraints:
  soft:
    faculty_workload_balance: 2.0
    minimize_travel_time: 1.5
    time_preference: 1.0
```

### Programmatic Configuration

```python
from src.optimization.nsga2_optimizer import OptimizationConfig

config = OptimizationConfig(
    population_size=200,
    num_generations=100,
    crossover_probability=0.8,
    mutation_probability=0.15
)

scheduler = TimetableScheduler()
scheduler.optimization_config = config
```

### Dynamic Rescheduling

```python
# Reschedule a specific course
course = scheduler.courses[0]
new_faculty = scheduler.faculty[1]

scheduler.dynamic_reschedule(
    course=course,
    new_faculty=new_faculty
)
```

### Export Formats

```python
# PDF (formatted text)
scheduler.export('output/timetable.pdf', format='pdf')

# Excel (multiple sheets)
scheduler.export('output/timetable.xlsx', format='excel')

# JSON (machine-readable)
scheduler.export('output/timetable.json', format='json')

# HTML (web view)
scheduler.export('output/timetable.html', format='html')

# iCalendar (calendar import)
scheduler.export('output/timetable.ical', format='ical')
```

## Troubleshooting

### No Feasible Solution Found

**Problem**: CSP solver cannot find a solution

**Solutions**:
1. Increase available time slots
2. Add more rooms
3. Reduce sessions per week for some courses
4. Use `hybrid` method instead of `csp`

### High Number of Conflicts

**Problem**: NSGA-II produces timetable with many conflicts

**Solutions**:
1. Increase population size: `population_size=200`
2. Increase generations: `num_generations=100`
3. Use hybrid method for better results
4. Run conflict resolution: `scheduler.resolve_conflicts()`

### Slow Performance

**Problem**: Optimization takes too long

**Solutions**:
1. Reduce population size and generations
2. Use CSP method for faster results
3. Reduce number of courses or time slots
4. Enable parallel processing (future feature)

### Import Errors

**Problem**: Module not found errors

**Solutions**:
1. Ensure virtual environment is activated
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (must be 3.8+)

### Invalid Data Format

**Problem**: Error loading CSV/Excel files

**Solutions**:
1. Verify column names match exactly
2. Check for missing required columns
3. Ensure no special characters in IDs
4. Validate data types (numbers as numbers, not text)

## Performance Tips

1. **Start Small**: Test with a subset of data first
2. **Use CSP First**: Quick feasibility check before optimization
3. **Tune Parameters**: Adjust population size vs. generations for speed/quality trade-off
4. **Cache Results**: Save good timetables for reuse
5. **Incremental Updates**: Use dynamic rescheduling for small changes

## Support

For issues, questions, or contributions:
- Check existing documentation
- Review example.py for usage patterns
- Examine data/*.csv for format examples

## License

MIT License - See LICENSE file for details
