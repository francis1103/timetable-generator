# System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                    AI-Powered Timetable Scheduler System                     │
└─────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────┐
│                              INPUT LAYER                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│  CSV Files    Excel Sheets    JSON Data    Natural Language Rules          │
│     ↓              ↓              ↓                ↓                         │
│  ┌──────────────────────────────────────────────────────┐                  │
│  │           Data Parsers (src/parsers/)                │                  │
│  │  • CSVParser  • ExcelParser  • NLPParser            │                  │
│  └──────────────────────────────────────────────────────┘                  │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                            DATA MODEL LAYER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌────────────────────────────────────────────────────────────────────┐    │
│  │              Core Models (src/models/)                             │    │
│  │  • Faculty    • Student    • Course    • Room    • TimeSlot       │    │
│  │  • Department • Schedule   • Timetable • ScheduleSlot             │    │
│  │  • Preference • PreferenceType                                     │    │
│  └────────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                         CONSTRAINT VALIDATION LAYER                          │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────┐  ┌──────────────────────────────────┐   │
│  │   Hard Constraints           │  │   Soft Constraints               │   │
│  │  (Must Never Violate)        │  │  (Optimization Targets)          │   │
│  ├──────────────────────────────┤  ├──────────────────────────────────┤   │
│  │  • No Room Overlap           │  │  • Faculty Workload Balance      │   │
│  │  • No Faculty Overlap        │  │  • Minimize Travel Time          │   │
│  │  • No Student Overlap        │  │  • Time Preferences              │   │
│  │  • Room Capacity             │  │  • Subject Spacing               │   │
│  │  • Faculty Availability      │  │  • Consecutive Class Limit       │   │
│  │  • Student Availability      │  │                                  │   │
│  │  • Max Subjects/Day          │  │  Weight: 0.0 - 2.0               │   │
│  │  Penalty: ∞                  │  │                                  │   │
│  └──────────────────────────────┘  └──────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                        OPTIMIZATION ENGINE LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐    │
│  │   NSGA-II       │  │   CSP Solver    │  │   ILP Solver            │    │
│  │   Optimizer     │  │                 │  │                         │    │
│  ├─────────────────┤  ├─────────────────┤  ├─────────────────────────┤    │
│  │ • Multi-obj GA  │  │ • Arc Consist.  │  │ • CBC Solver            │    │
│  │ • Pareto Front  │  │ • Domain Filter │  │ • Optimal Resolution    │    │
│  │ • Elitism       │  │ • Fast Feasible │  │ • Resource Allocation   │    │
│  │ • Pop: 100      │  │ • Backtracking  │  │ • Minimal Changes       │    │
│  │ • Gen: 50       │  │                 │  │                         │    │
│  │                 │  │                 │  │                         │    │
│  │ Time: 30-60s    │  │ Time: 5-15s     │  │ Time: 10-30s            │    │
│  │ Quality: ★★★★★  │  │ Quality: ★★★    │  │ Quality: ★★★★           │    │
│  └─────────────────┘  └─────────────────┘  └─────────────────────────┘    │
│                                    ↓                                         │
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │            Main Scheduler (src/optimization/scheduler.py)         │     │
│  │  • Orchestrates all optimization methods                          │     │
│  │  • Hybrid approach: CSP → NSGA-II → ILP                          │     │
│  │  • Conflict detection and resolution                              │     │
│  │  • Dynamic rescheduling                                           │     │
│  │  • AI recommendations                                             │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                          OUTPUT GENERATION LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌──────────────────────────────────────────────────────────────────┐      │
│  │                  Exporters (src/exporters/)                      │      │
│  │  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐        │      │
│  │  │  PDF   │ │ Excel  │ │  JSON  │ │  HTML  │ │  iCal  │        │      │
│  │  └────────┘ └────────┘ └────────┘ └────────┘ └────────┘        │      │
│  │     • Formatted  • Multi-sheet  • Machine   • Web     • Calendar│      │
│  │       reports      analysis      readable    view      sync     │      │
│  └──────────────────────────────────────────────────────────────────┘      │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                            API & INTERFACE LAYER                             │
├─────────────────────────────────────────────────────────────────────────────┤
│  ┌───────────────────────────────────────────────────────────────────┐     │
│  │              FastAPI REST API (src/api/main.py)                   │     │
│  │  ┌──────────────────────────────────────────────────────────┐    │     │
│  │  │  Endpoints:                                              │    │     │
│  │  │  POST /api/load-data          - Load scheduling data    │    │     │
│  │  │  POST /api/add-rule           - Add NL rule             │    │     │
│  │  │  POST /api/generate           - Generate timetable      │    │     │
│  │  │  GET  /api/timetable          - Get current schedule    │    │     │
│  │  │  GET  /api/conflicts          - Get conflict report     │    │     │
│  │  │  POST /api/resolve-conflicts  - Fix conflicts           │    │     │
│  │  │  GET  /api/recommendations    - Get AI suggestions      │    │     │
│  │  │  POST /api/export             - Export to file          │    │     │
│  │  │  WS   /ws                     - WebSocket updates       │    │     │
│  │  └──────────────────────────────────────────────────────────┘    │     │
│  │                                                                   │     │
│  │  Features:                                                        │     │
│  │  • CORS enabled  • Request validation  • Real-time updates      │     │
│  └───────────────────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────────────────┘
                                    ↓
┌─────────────────────────────────────────────────────────────────────────────┐
│                            CLIENT APPLICATIONS                               │
├─────────────────────────────────────────────────────────────────────────────┤
│   Python Scripts    │    Web Browsers    │    Mobile Apps    │   Integrations│
│   Command Line      │    JavaScript      │    REST Clients   │   Calendar Apps│
└─────────────────────────────────────────────────────────────────────────────┘


                        ┌──────────────────────────┐
                        │   Data Flow Example      │
                        └──────────────────────────┘
                                    
        CSV Data → Parser → Models → Constraints → NSGA-II Optimizer
                                                          ↓
                                            Generate Population
                                                          ↓
                                            Evaluate Fitness
                                                          ↓
                                        Selection & Breeding (50 gens)
                                                          ↓
                                            Pareto Front Solutions
                                                          ↓
                                            ILP Conflict Resolution
                                                          ↓
                                            Valid Timetable
                                                          ↓
                                            Export (PDF/Excel/etc)


                        ┌──────────────────────────┐
                        │   Fitness Evaluation     │
                        └──────────────────────────┘

    Timetable → Hard Constraint Check → Hard Violations Count
                                              ↓
                Soft Constraint Check → Weighted Penalty Sum
                                              ↓
                Preference Evaluation → Satisfaction Score
                                              ↓
                    Fitness = (hard_viol, soft_penalty, -pref_score)
                                              ↓
                            NSGA-II Ranking (Pareto)


                        ┌──────────────────────────┐
                        │   Technology Stack       │
                        └──────────────────────────┘

    Language:        Python 3.8+
    Algorithms:      DEAP (NSGA-II), python-constraint (CSP), PuLP (ILP)
    Web Framework:   FastAPI + Uvicorn
    Data Processing: pandas, numpy
    NLP:             spaCy, regex
    Export:          reportlab (PDF), openpyxl (Excel), icalendar
    Testing:         pytest
    API Docs:        Swagger/OpenAPI (auto-generated)
```
