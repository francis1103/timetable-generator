"""JSON exporter for timetables."""

from pathlib import Path
import json

from src.models.schedule import Timetable


class JSONExporter:
    """Export timetables to JSON format."""
    
    def export(self, timetable: Timetable, output_path: Path):
        """
        Export timetable to JSON.
        
        Args:
            timetable: Timetable to export
            output_path: Output JSON file path
        """
        # Prepare data
        data = {
            'metadata': {
                'generation_timestamp': timetable.generation_timestamp.isoformat(),
                'total_slots': timetable.get_total_slots(),
                'is_valid': timetable.is_valid(),
                'conflicts': len(timetable.conflicts),
            },
            'statistics': timetable.get_utilization_stats(),
            'fitness_scores': timetable.fitness_scores,
            'schedule': []
        }
        
        # Add schedule slots
        for slot in timetable.schedule_slots:
            slot_data = {
                'day': slot.time_slot.day.name,
                'start_time': slot.time_slot.start_time.strftime('%H:%M'),
                'end_time': slot.time_slot.end_time.strftime('%H:%M'),
                'course': {
                    'id': slot.course.course_id,
                    'code': slot.course.code,
                    'name': slot.course.name,
                    'credits': slot.course.credits,
                    'department': slot.course.department.name
                },
                'faculty': {
                    'id': slot.faculty.faculty_id,
                    'name': slot.faculty.name,
                    'email': slot.faculty.email,
                    'department': slot.faculty.department.name
                },
                'room': {
                    'id': slot.room.room_id,
                    'name': slot.room.name,
                    'building': slot.room.building,
                    'capacity': slot.room.capacity,
                    'type': slot.room.room_type.value
                },
                'students': {
                    'count': len(slot.students),
                    'ids': [s.student_id for s in slot.students]
                }
            }
            data['schedule'].append(slot_data)
        
        # Add conflicts if any
        if timetable.conflicts:
            data['conflicts'] = []
            for slot1, slot2, reasons in timetable.conflicts:
                data['conflicts'].append({
                    'course1': slot1.course.code,
                    'course2': slot2.course.code,
                    'reasons': reasons
                })
        
        # Write to file
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
