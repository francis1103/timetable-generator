"""Main timetable exporter coordinating all export formats."""

from typing import Optional
from pathlib import Path

from src.models.schedule import Timetable
from .pdf_exporter import PDFExporter
from .excel_exporter import ExcelExporter
from .json_exporter import JSONExporter


class TimetableExporter:
    """Main exporter class for timetables."""
    
    def __init__(self):
        """Initialize exporters."""
        self.pdf_exporter = PDFExporter()
        self.excel_exporter = ExcelExporter()
        self.json_exporter = JSONExporter()
    
    def export(self, timetable: Timetable, output_path: str, format: str = 'pdf'):
        """
        Export timetable to specified format.
        
        Args:
            timetable: Timetable to export
            output_path: Output file path
            format: Export format ('pdf', 'excel', 'json', 'ical', 'html')
        """
        output_file = Path(output_path)
        
        if format == 'pdf':
            self.pdf_exporter.export(timetable, output_file)
        elif format == 'excel':
            self.excel_exporter.export(timetable, output_file)
        elif format == 'json':
            self.json_exporter.export(timetable, output_file)
        elif format == 'ical':
            self._export_ical(timetable, output_file)
        elif format == 'html':
            self._export_html(timetable, output_file)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def _export_ical(self, timetable: Timetable, output_path: Path):
        """Export to iCalendar format."""
        from icalendar import Calendar, Event
        from datetime import datetime, timedelta
        
        cal = Calendar()
        cal.add('prodid', '-//Timetable Scheduler//EN')
        cal.add('version', '2.0')
        
        # Assuming current week for dates
        base_date = datetime.now().date()
        
        for slot in timetable.schedule_slots:
            event = Event()
            event.add('summary', f"{slot.course.code} - {slot.course.name}")
            event.add('location', f"{slot.room.building} - {slot.room.name}")
            event.add('description', f"Faculty: {slot.faculty.name}")
            
            # Calculate actual datetime
            day_offset = slot.time_slot.day.value
            event_date = base_date + timedelta(days=day_offset)
            
            start_dt = datetime.combine(event_date, slot.time_slot.start_time)
            end_dt = datetime.combine(event_date, slot.time_slot.end_time)
            
            event.add('dtstart', start_dt)
            event.add('dtend', end_dt)
            
            cal.add_component(event)
        
        with open(output_path, 'wb') as f:
            f.write(cal.to_ical())
    
    def _export_html(self, timetable: Timetable, output_path: Path):
        """Export to HTML format."""
        html = self._generate_html(timetable)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)
    
    def _generate_html(self, timetable: Timetable) -> str:
        """Generate HTML representation of timetable."""
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Timetable</title>
            <style>
                body { font-family: Arial, sans-serif; margin: 20px; }
                table { border-collapse: collapse; width: 100%; margin-top: 20px; }
                th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }
                th { background-color: #4CAF50; color: white; }
                tr:nth-child(even) { background-color: #f2f2f2; }
                .course-code { font-weight: bold; color: #2196F3; }
                .stats { margin: 20px 0; padding: 15px; background-color: #f9f9f9; border-radius: 5px; }
            </style>
        </head>
        <body>
            <h1>University Timetable</h1>
        """
        
        # Add statistics
        stats = timetable.get_utilization_stats()
        html += f"""
            <div class="stats">
                <h2>Statistics</h2>
                <p><strong>Total Slots:</strong> {timetable.get_total_slots()}</p>
                <p><strong>Total Rooms Used:</strong> {stats.get('total_rooms_used', 0)}</p>
                <p><strong>Total Faculty:</strong> {stats.get('total_faculty', 0)}</p>
                <p><strong>Average Faculty Hours:</strong> {stats.get('average_faculty_hours', 0):.2f}</p>
                <p><strong>Valid:</strong> {'✓ Yes' if timetable.is_valid() else '✗ No'}</p>
            </div>
        """
        
        # Add table
        html += """
            <table>
                <tr>
                    <th>Day</th>
                    <th>Time</th>
                    <th>Course</th>
                    <th>Faculty</th>
                    <th>Room</th>
                    <th>Students</th>
                </tr>
        """
        
        # Sort slots by day and time
        sorted_slots = sorted(
            timetable.schedule_slots,
            key=lambda s: (s.time_slot.day.value, s.time_slot.start_time)
        )
        
        for slot in sorted_slots:
            html += f"""
                <tr>
                    <td>{slot.time_slot.day.name}</td>
                    <td>{slot.time_slot.start_time.strftime('%H:%M')} - {slot.time_slot.end_time.strftime('%H:%M')}</td>
                    <td><span class="course-code">{slot.course.code}</span><br>{slot.course.name}</td>
                    <td>{slot.faculty.name}</td>
                    <td>{slot.room.building} - {slot.room.name}</td>
                    <td>{len(slot.students)}</td>
                </tr>
            """
        
        html += """
            </table>
        </body>
        </html>
        """
        
        return html
