import pandas as pd
from reportlab.lib.pagesizes import letter, landscape
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from datetime import datetime, timezone, timedelta
IST = timezone(timedelta(hours=5, minutes=30))
import os

class ReportGenerator:
    @staticmethod
    def generate_excel(data, output_path):
        """
        Generates a comprehensive, styled Excel file with multiple sheets.
        """
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            # ===== Sheet 1: Full Allocation Results =====
            df = pd.DataFrame(data)
            
            # Reorder columns for clarity
            priority_cols = [
                'Student ID', 'Name', 'Department', 'Class', 'Roll No',
                'Mobile', 'Email', 'Allocated Course', 'Preference Got', 'Status',
                'Submission Time',
                'Preference 1', 'Preference 2', 'Preference 3', 'Preference 4',
                'Preference 5', 'Preference 6', 'Preference 7', 'Preference 8'
            ]
            # Only keep columns that exist in data
            ordered_cols = [c for c in priority_cols if c in df.columns]
            remaining_cols = [c for c in df.columns if c not in ordered_cols]
            df = df[ordered_cols + remaining_cols]
            
            df.to_excel(writer, sheet_name='All Allocations', index=False)
            
            # Auto-size columns
            ws = writer.sheets['All Allocations']
            for col_idx, col_name in enumerate(df.columns, 1):
                max_len = max(
                    len(str(col_name)),
                    df[col_name].astype(str).str.len().max() if len(df) > 0 else 0
                )
                ws.column_dimensions[chr(64 + col_idx) if col_idx <= 26 else 'A'].width = min(max_len + 3, 35)

            # ===== Sheet 2: Course-wise Breakdown =====
            if 'Allocated Course' in df.columns:
                course_groups = df[df['Status'] == 'Allocated'].groupby('Allocated Course')
                course_summary = []
                
                for course_name, group in course_groups:
                    course_summary.append({
                        'Course': course_name,
                        'Students Allocated': len(group),
                        'Got 1st Preference': len(group[group['Preference Got'] == 1]),
                        'Got 2nd Preference': len(group[group['Preference Got'] == 2]),
                        'Got 3rd Preference': len(group[group['Preference Got'] == 3]),
                        'Got 4th+ Preference': len(group[group['Preference Got'].apply(
                            lambda x: isinstance(x, int) and x >= 4
                        )]),
                    })
                
                if course_summary:
                    cs_df = pd.DataFrame(course_summary)
                    cs_df.to_excel(writer, sheet_name='Course Summary', index=False)
                    
                # Individual course sheets
                for course_name, group in course_groups:
                    safe_name = course_name[:28].replace('/', '-')  # Sheet name max 31 chars
                    detail_cols = ['Student ID', 'Name', 'Department', 'Class', 'Roll No',
                                   'Mobile', 'Email', 'Preference Got', 'Submission Time']
                    existing_cols = [c for c in detail_cols if c in group.columns]
                    group[existing_cols].to_excel(writer, sheet_name=safe_name, index=False)

            # ===== Sheet 3: Unassigned Students =====
            unassigned = df[df['Status'] != 'Allocated']
            if len(unassigned) > 0:
                unassigned.to_excel(writer, sheet_name='Unassigned Students', index=False)

            # ===== Sheet 4: Summary Statistics =====
            total = len(df)
            assigned = len(df[df['Status'] == 'Allocated'])
            unassigned_count = total - assigned
            
            stats = {
                'Metric': [
                    'Total Students',
                    'Allocated Students',
                    'Unassigned Students',
                    'Allocation Rate (%)',
                    'Got 1st Preference',
                    'Got 2nd Preference',
                    'Got 3rd Preference',
                    'Got 4th+ Preference',
                    'Report Generated On'
                ],
                'Value': [
                    total,
                    assigned,
                    unassigned_count,
                    f"{(assigned / total * 100):.1f}%" if total > 0 else "0%",
                    len(df[df['Preference Got'] == 1]),
                    len(df[df['Preference Got'] == 2]),
                    len(df[df['Preference Got'] == 3]),
                    len(df[df['Preference Got'].apply(lambda x: isinstance(x, int) and x >= 4)]),
                    datetime.now(IST).strftime('%d %b %Y, %I:%M %p')
                ]
            }
            stats_df = pd.DataFrame(stats)
            stats_df.to_excel(writer, sheet_name='Summary', index=False)

            # ===== Sheet 5: Department-wise Breakdown =====
            if 'Department' in df.columns:
                dept_data = df[df['Status'] == 'Allocated'].groupby('Department').agg(
                    Students_Allocated=('Student ID', 'count'),
                ).reset_index()
                if len(dept_data) > 0:
                    dept_data.to_excel(writer, sheet_name='By Department', index=False)
        
        return output_path

    @staticmethod
    def generate_pdf(data, summary, output_path):
        """
        Generates a professional, multi-page PDF report.
        """
        doc = SimpleDocTemplate(
            output_path,
            pagesize=landscape(letter),
            leftMargin=40,
            rightMargin=40,
            topMargin=40,
            bottomMargin=40
        )
        
        styles = getSampleStyleSheet()
        elements = []
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle', parent=styles['Title'],
            fontSize=20, spaceAfter=6, alignment=TA_CENTER,
            textColor=colors.HexColor('#0f172a')
        )
        subtitle_style = ParagraphStyle(
            'CustomSubtitle', parent=styles['Normal'],
            fontSize=10, alignment=TA_CENTER, spaceAfter=20,
            textColor=colors.HexColor('#64748b')
        )
        heading_style = ParagraphStyle(
            'CustomHeading', parent=styles['Heading2'],
            fontSize=14, spaceAfter=10, spaceBefore=20,
            textColor=colors.HexColor('#0f172a')
        )
        normal_style = ParagraphStyle(
            'CustomNormal', parent=styles['Normal'],
            fontSize=9, textColor=colors.HexColor('#334155')
        )
        
        # ===== Page 1: Title & Summary =====
        elements.append(Spacer(1, 40))
        elements.append(Paragraph("Smart Course Allocation Report", title_style))
        elements.append(Paragraph(
            f"Generated on {datetime.now(IST).strftime('%d %B %Y, %I:%M %p')}",
            subtitle_style
        ))
        elements.append(Spacer(1, 20))
        
        # Summary table
        total = summary.get('total_students', 0)
        assigned = summary.get('assigned_students', 0)
        unassigned = summary.get('unassigned_students', 0)
        rate = summary.get('satisfaction_rate', 0)
        
        summary_data = [
            ['Metric', 'Value'],
            ['Total Students', str(total)],
            ['Allocated Students', str(assigned)],
            ['Unassigned Students', str(unassigned)],
            ['Allocation Rate', f"{rate:.1f}%"],
        ]
        
        # Count preference distribution
        pref_counts = {1: 0, 2: 0, 3: 0, '4+': 0}
        for item in data:
            pg = item.get('Preference Got', 'N/A')
            if pg == 1: pref_counts[1] += 1
            elif pg == 2: pref_counts[2] += 1
            elif pg == 3: pref_counts[3] += 1
            elif isinstance(pg, int) and pg >= 4: pref_counts['4+'] += 1
        
        summary_data.append(['Got 1st Preference', str(pref_counts[1])])
        summary_data.append(['Got 2nd Preference', str(pref_counts[2])])
        summary_data.append(['Got 3rd Preference', str(pref_counts[3])])
        summary_data.append(['Got 4th+ Preference', str(pref_counts['4+'])])
        
        summary_table = Table(summary_data, colWidths=[200, 150])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
            ('ALIGN', (1, 0), (1, -1), 'CENTER'),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
            ('TOPPADDING', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
        ]))
        elements.append(summary_table)
        
        # ===== Course Occupancy =====
        occupancy = summary.get('occupancy', {})
        if occupancy:
            elements.append(Paragraph("Course Occupancy", heading_style))
            
            occ_data = [['Course', 'Filled', 'Capacity', 'Occupancy %']]
            for name, info in occupancy.items():
                occ_data.append([
                    name,
                    str(info.get('filled', 0)),
                    str(info.get('capacity', 0)),
                    f"{info.get('percentage', 0):.1f}%"
                ])
            
            occ_table = Table(occ_data, colWidths=[220, 80, 80, 100])
            occ_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 9),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 8),
                ('ALIGN', (1, 0), (-1, -1), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 7),
                ('TOPPADDING', (0, 0), (-1, -1), 7),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
            ]))
            elements.append(occ_table)
        
        # ===== Page 2+: Full Student List =====
        elements.append(PageBreak())
        elements.append(Paragraph("Complete Allocation Details", heading_style))
        
        # Table headers
        table_headers = ['Student ID', 'Name', 'Department', 'Class', 'Roll No',
                         'Allocated Course', 'Pref #', 'Status', 'Submission Time']
        table_data = [table_headers]
        
        for item in data:
            row = [
                str(item.get('Student ID', '')),
                str(item.get('Name', ''))[:25],  # Truncate long names
                str(item.get('Department', '')),
                str(item.get('Class', '')),
                str(item.get('Roll No', '')),
                str(item.get('Allocated Course', '')),
                str(item.get('Preference Got', '')),
                str(item.get('Status', '')),
                str(item.get('Submission Time', ''))
            ]
            table_data.append(row)
        
        # Split into pages of ~30 rows each
        rows_per_page = 28
        for start in range(0, len(table_data), rows_per_page):
            chunk = table_data[start:start + rows_per_page]
            if start > 0:
                # Add header to each page chunk
                chunk = [table_headers] + chunk
                elements.append(PageBreak())
            
            col_widths = [70, 100, 80, 50, 50, 120, 40, 65, 130]
            student_table = Table(chunk, colWidths=col_widths, repeatRows=1)
            student_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0f172a')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 7.5),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 7),
                ('ALIGN', (6, 0), (6, -1), 'CENTER'),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.HexColor('#e2e8f0')),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')]),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ]))
            elements.append(student_table)
        
        # ===== Footer note =====
        elements.append(Spacer(1, 20))
        elements.append(Paragraph(
            "This report was auto-generated by the Smart Course Allocation System. "
            "For the detailed raw data, please refer to the Excel export.",
            ParagraphStyle('FootNote', parent=styles['Normal'],
                          fontSize=7, textColor=colors.HexColor('#94a3b8'),
                          alignment=TA_CENTER)
        ))
        
        doc.build(elements)
        return output_path
