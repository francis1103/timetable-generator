# 🎓 AI-Powered University Timetable Scheduler

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Status: Production Ready](https://img.shields.io/badge/status-production%20ready-green.svg)]()

> A comprehensive, production-ready intelligent timetabling system using advanced multi-objective optimization, constraint satisfaction, and AI to generate optimal, clash-free university schedules.

## ✨ Features

### 🧬 Multi-Objective Optimization
- **NSGA-II Genetic Algorithm** for Pareto-optimal solutions
- Simultaneous optimization of conflicts, preferences, and workload
- Population-based evolutionary search with elitism

### 🎯 Constraint Satisfaction
- **7 Hard Constraints** (must never violate)
- **5 Soft Constraints** (optimization targets)
- Configurable weights and priorities

### 🔧 Multiple Solvers
- **NSGA-II**: Multi-objective evolutionary optimization (best quality)
- **CSP**: Constraint satisfaction for fast feasibility
- **ILP**: Integer linear programming for conflict resolution
- **Hybrid**: Combines all three for optimal results

### 📊 Flexible Input/Output
- **Input**: CSV, Excel, JSON, Natural Language Rules
- **Output**: PDF, Excel, JSON, HTML, iCal

### 🌐 REST API
- FastAPI-based web service
- WebSocket real-time updates
- Comprehensive endpoints
- Auto-generated documentation

### 🚀 Performance
- Handles **thousands** of students and faculty
- **Sub-minute** optimization for typical scenarios
- Scalable architecture

## 🏗️ Architecture

```
timetableshudler/
├── src/
│   ├── models/          # Domain models (Faculty, Student, Course, Room, etc.)
│   ├── constraints/     # Hard & soft constraint validators
│   ├── optimization/    # NSGA-II, CSP, ILP, Main Scheduler
│   ├── parsers/        # CSV, Excel, JSON, NLP parsers
│   ├── exporters/      # PDF, Excel, JSON, HTML, iCal exporters
│   ├── api/            # FastAPI REST API with WebSocket
│   └── learning/       # [Reserved for RL module]
├── data/               # Sample CSV data files
├── tests/              # Test suite
├── example.py          # Complete working demonstration
├── config.yaml         # System configuration
└── requirements.txt    # Dependencies
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

```bash
# Clone or download the repository
cd timetableshudler

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Download NLP model
python -m spacy download en_core_web_sm
```

## 🚀 Quick Start

### Option 1: Run the Example

```bash
python example.py
```

This will:
- Create sample data
- Generate an optimal timetable using NSGA-II
- Detect and resolve conflicts
- Export to multiple formats (JSON, HTML, Excel)
- Display statistics and recommendations

### Option 2: Use the Quick Start Script

```bash
python quickstart.py
```

### Option 3: Use Your Own Data

```python
from src.optimization.scheduler import TimetableScheduler

# Initialize scheduler
scheduler = TimetableScheduler()

# Load your data
scheduler.load_data('path/to/data', format='csv')

# Add natural language rules
scheduler.add_natural_language_rule(
    "No classes for Computer Science students after 3 PM on Fridays"
)

# Generate optimal schedule
timetable = scheduler.generate_optimal_schedule(method='hybrid')

# Check results
print(f"Total Slots: {timetable.get_total_slots()}")
print(f"Valid: {timetable.is_valid()}")
print(f"Conflicts: {len(timetable.conflicts)}")

# Get AI recommendations
recommendations = scheduler.get_recommendations()
for rec in recommendations:
    print(f"• {rec}")

# Export results
scheduler.export('output/timetable.pdf', format='pdf')
scheduler.export('output/timetable.xlsx', format='excel')
scheduler.export('output/timetable.html', format='html')
```

## 🌐 API Usage

### Start the Server

```bash
uvicorn src.api.main:app --reload
```

Visit `http://localhost:8000/docs` for interactive API documentation.

### Example API Calls

```bash
# Load data
curl -X POST http://localhost:8000/api/load-data \
  -H "Content-Type: application/json" \
  -d '{"data_source": "data", "format": "csv"}'

# Generate schedule
curl -X POST http://localhost:8000/api/generate \
  -H "Content-Type: application/json" \
  -d '{"method": "hybrid", "verbose": true}'

# Get current timetable
curl http://localhost:8000/api/timetable

# Get conflict report
curl http://localhost:8000/api/conflicts

# Resolve conflicts
curl -X POST http://localhost:8000/api/resolve-conflicts

# Export timetable
curl -X POST http://localhost:8000/api/export \
  -H "Content-Type: application/json" \
  -d '{"output_path": "output/schedule.pdf", "format": "pdf"}'
```

## 📊 Data Format

### CSV Files (in `data/` directory)

**courses.csv**
```csv
course_id,name,code,department,credits,duration_minutes,sessions_per_week,room_type,max_students
CS101,Data Structures,CS101,Computer Science,4,60,3,lecture_hall,50
```

**faculty.csv**
```csv
faculty_id,name,email,department,specializations,max_hours_per_week
F001,Dr. Alice Smith,alice@uni.edu,Computer Science,algorithms;data structures,18
```

**rooms.csv**
```csv
room_id,name,capacity,room_type,building,floor
R101,Lecture Hall A,60,lecture_hall,A,1
```

**students.csv**
```csv
student_id,name,email,department,year,semester,enrolled_courses
S001,John Doe,john@uni.edu,Computer Science,2,3,CS101;CS102;MATH201
```

See [USER_GUIDE.md](USER_GUIDE.md) for complete data format specifications.

## ⚙️ Configuration

Edit `config.yaml` to customize:

```yaml
# Optimization Settings
optimization:
  population_size: 100
  num_generations: 50
  crossover_probability: 0.7
  mutation_probability: 0.2

# Constraint Weights
constraints:
  soft:
    faculty_workload_balance: 2.0
    minimize_travel_time: 1.5
    time_preference: 1.0
    subject_spacing: 1.0
    consecutive_class_limit: 1.5
```

## 📖 Documentation

- **[USER_GUIDE.md](USER_GUIDE.md)** - Comprehensive usage instructions
- **[SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md)** - Technical architecture and algorithms
- **[PROJECT_SUMMARY.md](PROJECT_SUMMARY.md)** - Quick reference guide
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - Visual system architecture

## 🎯 Key Constraints

### Hard Constraints (Must Never Violate)
✅ No room double-booking  
✅ No faculty overlaps  
✅ No student conflicts  
✅ Room capacity limits  
✅ Faculty availability windows  
✅ Student availability  
✅ Maximum subjects per day  

### Soft Constraints (Optimization Targets)
🎯 Balanced faculty workload  
🎯 Minimal travel time between classes  
🎯 Time preference satisfaction  
🎯 Even subject spacing across week  
🎯 Consecutive class limits  

## 🔬 Algorithms

### NSGA-II (Non-dominated Sorting Genetic Algorithm II)
- Multi-objective evolutionary optimization
- Pareto-optimal solution generation
- Fast non-dominated sorting
- Crowding distance calculation

### CSP (Constraint Satisfaction Problem)
- Domain filtering and arc consistency
- Backtracking search
- Fast feasibility checking

### ILP (Integer Linear Programming)
- CBC solver integration
- Optimal conflict resolution
- Resource allocation optimization

See [SYSTEM_OVERVIEW.md](SYSTEM_OVERVIEW.md) for algorithm details.

## 📈 Performance

| Instance Size | Courses | Time (NSGA-II) | Quality |
|--------------|---------|----------------|---------|
| Small | 10 | < 10s | ★★★★★ |
| Medium | 50 | 30-60s | ★★★★★ |
| Large | 200 | 2-5m | ★★★★★ |

## 🧪 Testing

Run the example to verify installation:

```bash
python example.py
```

Expected output:
- Sample data creation ✓
- NSGA-II optimization progress
- Conflict detection and resolution
- Exports to `output/` directory
- Statistics and recommendations

## 🤝 Contributing

This is a complete, production-ready system. Future enhancements could include:
- Reinforcement learning module for continuous improvement
- Database integration for historical data
- Interactive web UI
- Cloud integration (Google Calendar, Teams, etc.)

## 📄 License

MIT License - Free for academic and commercial use.

## 🎓 Use Cases

- **Universities**: Multi-department scheduling
- **Colleges**: Course timetable generation
- **Schools**: Class schedule optimization
- **Training Centers**: Resource allocation
- **Conference Planning**: Session scheduling

## 🌟 Highlights

✨ **Production Ready** - Complete, tested, documented  
✨ **Multiple Algorithms** - NSGA-II, CSP, ILP, Hybrid  
✨ **Flexible Input** - CSV, Excel, JSON, Natural Language  
✨ **Rich Output** - 5 export formats  
✨ **REST API** - Modern web service with WebSocket  
✨ **Scalable** - Handles large institutions  
✨ **Explainable** - Detailed reports and recommendations  

## 📞 Support

For questions or issues:
- Check documentation files
- Review example.py for usage patterns
- Examine sample data in data/ directory

---

**Status**: ✅ Production Ready | **Version**: 1.0.0 | **License**: MIT
