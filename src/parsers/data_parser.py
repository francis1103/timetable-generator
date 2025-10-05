"""Main data parser for handling multiple input formats."""

from typing import Dict, List, Any
from pathlib import Path
import pandas as pd
import json

from src.models.entities import (
    Course, Faculty, Room, TimeSlot, Student, Department,
    RoomType, DayOfWeek
)
from datetime import time


class DataParser:
    """Main parser for loading scheduling data from various formats."""
    
    def parse(self, data_source: str, format: str = 'auto') -> Dict[str, List]:
        """
        Parse scheduling data from various sources.
        
        Args:
            data_source: Path to data file or directory
            format: Data format ('csv', 'excel', 'json', 'auto')
            
        Returns:
            Dictionary with courses, faculty, rooms, time_slots, students
        """
        path = Path(data_source)
        
        if format == 'auto':
            format = self._detect_format(path)
        
        if format == 'csv':
            return self._parse_csv(path)
        elif format == 'excel':
            return self._parse_excel(path)
        elif format == 'json':
            return self._parse_json(path)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _detect_format(self, path: Path) -> str:
        """Detect file format from extension."""
        suffix = path.suffix.lower()
        
        if suffix == '.csv':
            return 'csv'
        elif suffix in ['.xlsx', '.xls']:
            return 'excel'
        elif suffix == '.json':
            return 'json'
        elif path.is_dir():
            # Check for CSV files in directory
            if list(path.glob('*.csv')):
                return 'csv'
        
        return 'csv'  # Default
    
    def _parse_csv(self, path: Path) -> Dict[str, List]:
        """Parse CSV files."""
        data = {
            'courses': [],
            'faculty': [],
            'rooms': [],
            'time_slots': [],
            'students': [],
            'departments': []
        }
        
        if path.is_dir():
            # Look for specific CSV files
            courses_file = path / 'courses.csv'
            faculty_file = path / 'faculty.csv'
            rooms_file = path / 'rooms.csv'
            students_file = path / 'students.csv'
            
            if courses_file.exists():
                data['courses'] = self._parse_courses_csv(courses_file)
            
            if faculty_file.exists():
                data['faculty'] = self._parse_faculty_csv(faculty_file)
            
            if rooms_file.exists():
                data['rooms'] = self._parse_rooms_csv(rooms_file)
            
            if students_file.exists():
                data['students'] = self._parse_students_csv(students_file)
        
        # Generate default time slots
        data['time_slots'] = self._generate_default_timeslots()
        
        return data
    
    def _parse_courses_csv(self, file_path: Path) -> List[Course]:
        """Parse courses from CSV."""
        df = pd.read_csv(file_path)
        courses = []
        
        for _, row in df.iterrows():
            # Create department
            dept = Department(
                dept_id=row.get('department_id', 'DEPT001'),
                name=row.get('department', 'General')
            )
            
            course = Course(
                course_id=str(row['course_id']),
                name=row['name'],
                code=row['code'],
                department=dept,
                credits=int(row.get('credits', 3)),
                duration_minutes=int(row.get('duration_minutes', 60)),
                sessions_per_week=int(row.get('sessions_per_week', 2)),
                required_room_type=RoomType(row.get('room_type', 'lecture_hall')),
                max_students=int(row.get('max_students', 100)),
                is_lab=bool(row.get('is_lab', False))
            )
            
            courses.append(course)
        
        return courses
    
    def _parse_faculty_csv(self, file_path: Path) -> List[Faculty]:
        """Parse faculty from CSV."""
        df = pd.read_csv(file_path)
        faculty = []
        
        for _, row in df.iterrows():
            dept = Department(
                dept_id=row.get('department_id', 'DEPT001'),
                name=row.get('department', 'General')
            )
            
            specializations = set()
            if 'specializations' in row and pd.notna(row['specializations']):
                specializations = set(str(row['specializations']).split(';'))
            
            fac = Faculty(
                faculty_id=str(row['faculty_id']),
                name=row['name'],
                email=row.get('email', f"{row['faculty_id']}@university.edu"),
                department=dept,
                specializations=specializations,
                max_hours_per_week=int(row.get('max_hours_per_week', 20)),
                max_consecutive_classes=int(row.get('max_consecutive_classes', 3))
            )
            
            faculty.append(fac)
        
        return faculty
    
    def _parse_rooms_csv(self, file_path: Path) -> List[Room]:
        """Parse rooms from CSV."""
        df = pd.read_csv(file_path)
        rooms = []
        
        for _, row in df.iterrows():
            facilities = set()
            if 'facilities' in row and pd.notna(row['facilities']):
                facilities = set(str(row['facilities']).split(';'))
            
            room = Room(
                room_id=str(row['room_id']),
                name=row['name'],
                capacity=int(row['capacity']),
                room_type=RoomType(row.get('room_type', 'lecture_hall')),
                building=row.get('building', 'Main'),
                floor=int(row.get('floor', 1)),
                facilities=facilities
            )
            
            rooms.append(room)
        
        return rooms
    
    def _parse_students_csv(self, file_path: Path) -> List[Student]:
        """Parse students from CSV."""
        df = pd.read_csv(file_path)
        students = []
        
        for _, row in df.iterrows():
            dept = Department(
                dept_id=row.get('department_id', 'DEPT001'),
                name=row.get('department', 'General')
            )
            
            enrolled_courses = set()
            if 'enrolled_courses' in row and pd.notna(row['enrolled_courses']):
                enrolled_courses = set(str(row['enrolled_courses']).split(';'))
            
            student = Student(
                student_id=str(row['student_id']),
                name=row['name'],
                email=row.get('email', f"{row['student_id']}@university.edu"),
                department=dept,
                year=int(row.get('year', 1)),
                semester=int(row.get('semester', 1)),
                enrolled_courses=enrolled_courses,
                max_subjects_per_day=int(row.get('max_subjects_per_day', 5))
            )
            
            students.append(student)
        
        return students
    
    def _parse_excel(self, file_path: Path) -> Dict[str, List]:
        """Parse Excel file with multiple sheets."""
        data = {
            'courses': [],
            'faculty': [],
            'rooms': [],
            'time_slots': [],
            'students': []
        }
        
        excel_file = pd.ExcelFile(file_path)
        
        if 'courses' in excel_file.sheet_names:
            df = pd.read_excel(excel_file, 'courses')
            temp_path = Path('temp_courses.csv')
            df.to_csv(temp_path, index=False)
            data['courses'] = self._parse_courses_csv(temp_path)
            temp_path.unlink()
        
        if 'faculty' in excel_file.sheet_names:
            df = pd.read_excel(excel_file, 'faculty')
            temp_path = Path('temp_faculty.csv')
            df.to_csv(temp_path, index=False)
            data['faculty'] = self._parse_faculty_csv(temp_path)
            temp_path.unlink()
        
        if 'rooms' in excel_file.sheet_names:
            df = pd.read_excel(excel_file, 'rooms')
            temp_path = Path('temp_rooms.csv')
            df.to_csv(temp_path, index=False)
            data['rooms'] = self._parse_rooms_csv(temp_path)
            temp_path.unlink()
        
        if 'students' in excel_file.sheet_names:
            df = pd.read_excel(excel_file, 'students')
            temp_path = Path('temp_students.csv')
            df.to_csv(temp_path, index=False)
            data['students'] = self._parse_students_csv(temp_path)
            temp_path.unlink()
        
        data['time_slots'] = self._generate_default_timeslots()
        
        return data
    
    def _parse_json(self, file_path: Path) -> Dict[str, List]:
        """Parse JSON file."""
        with open(file_path, 'r') as f:
            json_data = json.load(f)
        
        # Convert JSON to objects
        # (Simplified - full implementation would handle all fields)
        
        return {
            'courses': [],
            'faculty': [],
            'rooms': [],
            'time_slots': self._generate_default_timeslots(),
            'students': []
        }
    
    def _generate_default_timeslots(self) -> List[TimeSlot]:
        """Generate default time slots for a week."""
        slots = []
        
        days = [DayOfWeek.MONDAY, DayOfWeek.TUESDAY, DayOfWeek.WEDNESDAY,
                DayOfWeek.THURSDAY, DayOfWeek.FRIDAY]
        
        # Morning slots (8 AM - 12 PM)
        times = [
            (time(8, 0), time(9, 0)),
            (time(9, 0), time(10, 0)),
            (time(10, 0), time(11, 0)),
            (time(11, 0), time(12, 0)),
            (time(12, 0), time(13, 0)),
            # Afternoon slots (2 PM - 5 PM)
            (time(14, 0), time(15, 0)),
            (time(15, 0), time(16, 0)),
            (time(16, 0), time(17, 0)),
        ]
        
        for day in days:
            for start, end in times:
                slot = TimeSlot(day=day, start_time=start, end_time=end)
                slots.append(slot)
        
        return slots
    
    def parse_natural_language_rule(self, rule: str) -> Dict[str, Any]:
        """
        Parse natural language scheduling rule.
        
        Args:
            rule: Natural language rule
            
        Returns:
            Parsed constraint specification
        """
        # This would use NLP (spaCy, transformers) to parse the rule
        # Simplified placeholder implementation
        
        from .nlp_parser import NLPParser
        
        nlp_parser = NLPParser()
        return nlp_parser.parse_rule(rule)
