"""Excel exporter for timetables."""

from pathlib import Path
import pandas as pd

from src.models.schedule import Timetable


class ExcelExporter:
    """Export timetables to Excel format."""
    
    def export(self, timetable: Timetable, output_path: Path):
        """
        Export timetable to Excel.
        
        Args:
            timetable: Timetable to export
            output_path: Output Excel file path
        """
        # Prepare data
        data = []
        
        sorted_slots = sorted(
            timetable.schedule_slots,
            key=lambda s: (s.time_slot.day.value, s.time_slot.start_time)
        )
        
        for slot in sorted_slots:
            row = {
                'Day': slot.time_slot.day.name,
                'Start Time': slot.time_slot.start_time.strftime('%H:%M'),
                'End Time': slot.time_slot.end_time.strftime('%H:%M'),
                'Course Code': slot.course.code,
                'Course Name': slot.course.name,
                'Faculty': slot.faculty.name,
                'Room': f"{slot.room.building} - {slot.room.name}",
                'Capacity': slot.room.capacity,
                'Students': len(slot.students),
                'Department': slot.course.department.name
            }
            data.append(row)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Create Excel writer with multiple sheets
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # Main timetable
            df.to_excel(writer, sheet_name='Timetable', index=False)
            
            # Statistics sheet
            stats = timetable.get_utilization_stats()
            stats_df = pd.DataFrame([
                {'Metric': 'Total Slots', 'Value': timetable.get_total_slots()},
                {'Metric': 'Total Rooms Used', 'Value': stats.get('total_rooms_used', 0)},
                {'Metric': 'Total Faculty', 'Value': stats.get('total_faculty', 0)},
                {'Metric': 'Average Faculty Hours', 'Value': f"{stats.get('average_faculty_hours', 0):.2f}"},
                {'Metric': 'Valid Schedule', 'Value': 'Yes' if timetable.is_valid() else 'No'}
            ])
            stats_df.to_excel(writer, sheet_name='Statistics', index=False)
            
            # Conflicts sheet (if any)
            conflicts = timetable.detect_conflicts()
            if conflicts:
                conflict_data = []
                for slot1, slot2, reasons in conflicts:
                    conflict_data.append({
                        'Course 1': slot1.course.code,
                        'Course 2': slot2.course.code,
                        'Conflict Type': ', '.join(reasons)
                    })
                conflict_df = pd.DataFrame(conflict_data)
                conflict_df.to_excel(writer, sheet_name='Conflicts', index=False)
