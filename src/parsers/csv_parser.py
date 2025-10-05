"""CSV-specific parsing utilities."""

import pandas as pd
from pathlib import Path
from typing import List

from src.models.entities import Course, Faculty, Room, Student


class CSVParser:
    """Specialized CSV parser with validation."""
    
    @staticmethod
    def validate_courses_csv(file_path: Path) -> bool:
        """Validate courses CSV format."""
        required_columns = ['course_id', 'name', 'code']
        
        try:
            df = pd.read_csv(file_path)
            return all(col in df.columns for col in required_columns)
        except Exception:
            return False
    
    @staticmethod
    def validate_faculty_csv(file_path: Path) -> bool:
        """Validate faculty CSV format."""
        required_columns = ['faculty_id', 'name']
        
        try:
            df = pd.read_csv(file_path)
            return all(col in df.columns for col in required_columns)
        except Exception:
            return False
