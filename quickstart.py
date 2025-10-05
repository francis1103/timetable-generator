"""
Quick start script for the AI-Powered Timetable Scheduler.
Run this to see the system in action!
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

def main():
    print("="*80)
    print("🎓 AI-Powered Timetable Scheduler - Quick Start")
    print("="*80)
    print()
    
    print("This system provides:")
    print("  ✅ Multi-objective optimization (NSGA-II)")
    print("  ✅ Constraint satisfaction (CSP)")
    print("  ✅ Conflict resolution (ILP)")
    print("  ✅ Natural language rule parsing")
    print("  ✅ Multiple export formats (PDF, Excel, JSON, HTML, iCal)")
    print("  ✅ REST API with WebSocket support")
    print()
    
    print("Quick Start Options:")
    print()
    print("1. Run Example Demonstration")
    print("   python example.py")
    print()
    print("2. Start REST API Server")
    print("   uvicorn src.api.main:app --reload")
    print()
    print("3. Use Programmatically")
    print("   from src.optimization.scheduler import TimetableScheduler")
    print("   scheduler = TimetableScheduler()")
    print("   scheduler.load_data('data', format='csv')")
    print("   timetable = scheduler.generate_optimal_schedule()")
    print()
    
    print("="*80)
    print("📚 Documentation:")
    print("  • README.md - Overview")
    print("  • USER_GUIDE.md - Detailed usage instructions")
    print("  • SYSTEM_OVERVIEW.md - Technical architecture")
    print("  • PROJECT_SUMMARY.md - Quick reference")
    print("="*80)
    print()
    
    choice = input("Would you like to run the example demonstration? (y/n): ")
    
    if choice.lower() == 'y':
        print("\n🚀 Starting example demonstration...\n")
        from example import main as run_example
        run_example()
    else:
        print("\n👋 Goodbye! Check the documentation for more options.")

if __name__ == "__main__":
    main()
