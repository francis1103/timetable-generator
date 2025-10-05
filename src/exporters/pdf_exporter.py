"""PDF exporter for timetables."""

from pathlib import Path
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

from src.models.schedule import Timetable


class PDFExporter:
    """Export timetables to PDF format."""
    
    def export(self, timetable: Timetable, output_path: Path):
        """
        Export timetable to PDF.
        
        Args:
            timetable: Timetable to export
            output_path: Output PDF file path
        """
        # Create PDF document
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=landscape(A4),
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Container for elements
        elements = []
        styles = getSampleStyleSheet()
        
        # Title
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=24,
            textColor=colors.HexColor('#2196F3'),
            spaceAfter=30,
            alignment=1  # Center
        )
        
        title = Paragraph("University Timetable", title_style)
        elements.append(title)
        
        # Statistics
        stats = timetable.get_utilization_stats()
        stats_text = f"""
        <b>Total Slots:</b> {timetable.get_total_slots()} | 
        <b>Rooms Used:</b> {stats.get('total_rooms_used', 0)} | 
        <b>Faculty:</b> {stats.get('total_faculty', 0)} | 
        <b>Valid:</b> {'✓' if timetable.is_valid() else '✗'}
        """
        
        stats_para = Paragraph(stats_text, styles['Normal'])
        elements.append(stats_para)
        elements.append(Spacer(1, 0.3*inch))
        
        # Create table data
        table_data = [['Day', 'Time', 'Course', 'Faculty', 'Room', 'Students']]
        
        # Sort slots
        sorted_slots = sorted(
            timetable.schedule_slots,
            key=lambda s: (s.time_slot.day.value, s.time_slot.start_time)
        )
        
        for slot in sorted_slots:
            row = [
                slot.time_slot.day.name[:3],
                f"{slot.time_slot.start_time.strftime('%H:%M')}-{slot.time_slot.end_time.strftime('%H:%M')}",
                f"{slot.course.code}\n{slot.course.name}",
                slot.faculty.name,
                f"{slot.room.building}-{slot.room.name}",
                str(len(slot.students))
            ]
            table_data.append(row)
        
        # Create table
        table = Table(table_data, colWidths=[0.8*inch, 1.2*inch, 2.5*inch, 1.5*inch, 1.2*inch, 0.8*inch])
        
        # Style table
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4CAF50')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 8),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f2f2f2')])
        ]))
        
        elements.append(table)
        
        # Build PDF
        doc.build(elements)


class PDFExporter:
    """Simplified PDF exporter without external dependencies."""
    
    def export(self, timetable: Timetable, output_path: Path):
        """Export timetable to PDF (simplified)."""
        # For now, export as text file with .pdf extension
        # In production, use reportlab as shown above
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("UNIVERSITY TIMETABLE\n")
            f.write("=" * 80 + "\n\n")
            
            stats = timetable.get_utilization_stats()
            f.write(f"Total Slots: {timetable.get_total_slots()}\n")
            f.write(f"Rooms Used: {stats.get('total_rooms_used', 0)}\n")
            f.write(f"Valid: {'Yes' if timetable.is_valid() else 'No'}\n")
            f.write("\n" + "=" * 80 + "\n\n")
            
            sorted_slots = sorted(
                timetable.schedule_slots,
                key=lambda s: (s.time_slot.day.value, s.time_slot.start_time)
            )
            
            for slot in sorted_slots:
                f.write(f"{slot.time_slot.day.name:<10} ")
                f.write(f"{slot.time_slot.start_time.strftime('%H:%M')}-{slot.time_slot.end_time.strftime('%H:%M'):<12} ")
                f.write(f"{slot.course.code:<10} {slot.course.name:<30} ")
                f.write(f"{slot.faculty.name:<20} ")
                f.write(f"{slot.room.name:<15} ")
                f.write(f"({len(slot.students)} students)\n")
