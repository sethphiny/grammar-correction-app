import os
import tempfile
from datetime import datetime
from typing import List, Dict
from docx import Document
from docx.shared import Inches, Pt
from docx.enum.text import WD_ALIGN_PARAGRAPH
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib import colors

from models.schemas import GrammarIssue

class ReportGenerator:
    """Generates correction reports in DOCX and PDF formats"""
    
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
    
    async def generate_report(
        self,
        issues: List[GrammarIssue],
        summary: Dict,
        original_filename: str,
        output_format: str = "docx",
        output_filename: str = "grammar_report"
    ) -> str:
        """Generate a correction report"""
        
        if output_format.lower() == "docx":
            return await self._generate_docx_report(issues, summary, original_filename, output_filename)
        elif output_format.lower() == "pdf":
            return await self._generate_pdf_report(issues, summary, original_filename, output_filename)
        else:
            raise ValueError(f"Unsupported output format: {output_format}")
    
    async def _generate_docx_report(
        self,
        issues: List[GrammarIssue],
        summary: Dict,
        original_filename: str,
        output_filename: str
    ) -> str:
        """Generate DOCX report"""
        doc = Document()
        
        # Set document margins
        sections = doc.sections
        for section in sections:
            section.top_margin = Inches(1)
            section.bottom_margin = Inches(1)
            section.left_margin = Inches(1)
            section.right_margin = Inches(1)
        
        # Document Header Section
        self._add_document_header(doc, original_filename)
        
        # Title - match sample format
        title = doc.add_heading('Issues by Line Number', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.LEFT
        
        # Issues section
        if issues:
            # Group issues by line range for better organization
            issues_by_line_range = {}
            for issue in issues:
                # Use line_range if available, otherwise fall back to line_number
                line_key = getattr(issue, 'line_range', None) or str(issue.line_number)
                if line_key not in issues_by_line_range:
                    issues_by_line_range[line_key] = []
                issues_by_line_range[line_key].append(issue)
            
            # Sort by line number (extract numeric part for sorting)
            def extract_line_number(line_key):
                if '–' in str(line_key):
                    return int(str(line_key).split('–')[0])
                return int(line_key)
            
            sorted_line_keys = sorted(issues_by_line_range.keys(), key=extract_line_number)
            
            for line_key in sorted_line_keys:
                line_issues = issues_by_line_range[line_key]
                
                # Line header - format as "Line X–Y" or "Line X"
                line_header = doc.add_paragraph()
                line_run = line_header.add_run(f"Line {line_key}")
                line_run.bold = True
                line_run.font_size = Pt(12)
                
                for issue in line_issues:
                    # Quote the problematic text
                    quote_para = doc.add_paragraph(f'“{issue.original_text}”')
                    quote_para.paragraph_format.left_indent = Inches(0.25)
                    quote_para.paragraph_format.space_after = Pt(2)
                    quote_run = quote_para.runs[0]
                    quote_run.italic = True
                    
                    # Problem line
                    problem_para = doc.add_paragraph(f"• Problem: {issue.problem}")
                    problem_para.paragraph_format.left_indent = Inches(0.5)
                    problem_para.paragraph_format.space_after = Pt(0)
                    
                    # Fix line
                    fix_para = doc.add_paragraph(f'• Fix: → “{issue.proposed_fix.corrected_text}”')
                    fix_para.paragraph_format.left_indent = Inches(0.5)
                    fix_para.paragraph_format.space_after = Pt(10)
                
                doc.add_paragraph()  # Empty line between line groups
        
        # Summary section
        doc.add_heading('✅ Summary', level=1)
        
        # Build summary items based on what was actually found
        summary_items = []
        
        if summary.get('verb_tense_consistency', 0) > 0:
            count = summary['verb_tense_consistency']
            summary_items.append(f"Verb tense & agreement: {count} issue{'s' if count != 1 else ''} (tense consistency, subject-verb agreement)")
        
        if summary.get('awkward_phrasing', 0) > 0:
            count = summary['awkward_phrasing']
            summary_items.append(f"Style & clarity: {count} issue{'s' if count != 1 else ''} (awkward phrasing, unclear constructions)")
        
        if summary.get('redundancy', 0) > 0:
            count = summary['redundancy']
            summary_items.append(f"Wordiness & redundancy: {count} issue{'s' if count != 1 else ''} (repetitive phrases, unnecessary words)")
        
        if summary.get('grammar_punctuation', 0) > 0:
            count = summary['grammar_punctuation']
            summary_items.append(f"Grammar & punctuation: {count} issue{'s' if count != 1 else ''} (commas, quotation marks, apostrophes, spelling)")
        
        if summary_items:
            doc.add_paragraph("The main issues found in your document:")
            for item in summary_items:
                doc.add_paragraph(item)
        else:
            doc.add_paragraph("No issues found in your document.")
        
        # Save document
        output_path = os.path.join(self.temp_dir, f"{output_filename}.docx")
        doc.save(output_path)
        
        return output_path
    
    def _add_document_header(self, doc: Document, original_filename: str):
        """Add a comprehensive document header with metadata"""
        
        # Main title
        title = doc.add_heading('Grammar Correction Report', 0)
        title.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        # Add spacing
        doc.add_paragraph()
        
        # Document information table
        table = doc.add_table(rows=6, cols=2)
        table.style = 'Table Grid'
        
        # Set column widths
        table.columns[0].width = Inches(2.0)
        table.columns[1].width = Inches(4.0)
        
        # Document metadata
        metadata = [
            ("Document:", original_filename),
            ("Date:", datetime.now().strftime("%B %d, %Y")),
            ("Time:", datetime.now().strftime("%I:%M %p")),
            ("Report Type:", "Grammar & Style Analysis"),
            ("Format:", "Detailed Line-by-Line Review"),
            ("Status:", "Completed")
        ]
        
        for i, (label, value) in enumerate(metadata):
            # Label cell
            label_cell = table.rows[i].cells[0]
            label_para = label_cell.paragraphs[0]
            label_run = label_para.add_run(label)
            label_run.bold = True
            label_run.font_size = Pt(11)
            
            # Value cell
            value_cell = table.rows[i].cells[1]
            value_para = value_cell.paragraphs[0]
            value_run = value_para.add_run(value)
            value_run.font_size = Pt(11)
        
        # Add spacing after header
        doc.add_paragraph()
        doc.add_paragraph()
        
        # Add a brief description
        desc_para = doc.add_paragraph()
        desc_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        desc_run = desc_para.add_run(
            "This report provides a comprehensive analysis of grammar, punctuation, style, and clarity issues found in your document. "
            "Each issue includes the problem description, suggested fix, and corrected text for easy review and implementation."
        )
        desc_run.font_size = Pt(11)
        desc_run.italic = True
        
        # Add separator line
        doc.add_paragraph()
        separator = doc.add_paragraph("─" * 80)
        separator.alignment = WD_ALIGN_PARAGRAPH.CENTER
        separator_run = separator.runs[0]
        separator_run.font_size = Pt(10)
        separator_run.font.color.rgb = None  # Use default color
        
        # Add spacing before main content
        doc.add_paragraph()
        doc.add_paragraph()
    
    async def _generate_pdf_report(
        self,
        issues: List[GrammarIssue],
        summary: Dict,
        original_filename: str,
        output_filename: str
    ) -> str:
        """Generate PDF report"""
        output_path = os.path.join(self.temp_dir, f"{output_filename}.pdf")
        
        doc = SimpleDocTemplate(
            output_path,
            pagesize=letter,
            rightMargin=inch,
            leftMargin=inch,
            topMargin=inch,
            bottomMargin=inch
        )
        
        # Get styles
        styles = getSampleStyleSheet()
        
        # Custom styles
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1  # Center alignment
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=14,
            spaceAfter=12
        )
        
        normal_style = ParagraphStyle(
            'CustomNormal',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=6,
            spaceBefore=0
        )
        
        bullet_style = ParagraphStyle(
            'CustomBullet',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            spaceBefore=0,
            leftIndent=18,
            firstLineIndent=-18
        )
        
        reason_style = ParagraphStyle(
            'CustomReason',
            parent=styles['Normal'],
            fontSize=11,
            spaceAfter=4,
            spaceBefore=0,
            leftIndent=36,
            firstLineIndent=-18
        )
        
        # Build content
        story = []
        
        # Title
        story.append(Paragraph("Grammar Correction Report", title_style))
        
        # Document info table
        story.append(Spacer(1, 12))
        
        # Create a table-like structure for metadata
        metadata_items = [
            ("Document:", original_filename),
            ("Date:", datetime.now().strftime("%B %d, %Y")),
            ("Time:", datetime.now().strftime("%I:%M %p")),
            ("Report Type:", "Grammar & Style Analysis"),
            ("Format:", "Detailed Line-by-Line Review"),
            ("Status:", "Completed"),
            ("Total Issues Found:", str(summary.get('total_issues', 0)))
        ]
        
        for label, value in metadata_items:
            story.append(Paragraph(f"<b>{label}</b> {value}", normal_style))
        
        # Add description
        story.append(Spacer(1, 12))
        desc_text = (
            "This report provides a comprehensive analysis of grammar, punctuation, style, and clarity issues found in your document. "
            "Each issue includes the problem description, suggested fix, and corrected text for easy review and implementation."
        )
        story.append(Paragraph(f"<i>{desc_text}</i>", normal_style))
        
        story.append(Spacer(1, 20))
        
        # Issues section
        if issues:
            story.append(Paragraph("Issues Found", heading_style))
            
            # Group issues by line number for better organization
            issues_by_line = {}
            for issue in issues:
                line_key = issue.line_number
                if line_key not in issues_by_line:
                    issues_by_line[line_key] = []
                issues_by_line[line_key].append(issue)
            
            # Sort by line number
            for line_number in sorted(issues_by_line.keys()):
                line_issues = issues_by_line[line_number]
                
                # Line header - format as "Line X, Sentence Y"
                story.append(Paragraph(f"<b>Line {line_number}, Sentence {line_issues[0].sentence_number}</b>", normal_style))
                
                for issue in line_issues:
                    # Original text
                    story.append(Paragraph(f'<i>"{issue.original_text}"</i>', normal_style))
                    
                    # Handle Problem/Reason format properly
                    if '\n' in issue.problem:
                        # Split problem into Problem and Reason
                        problem_lines = issue.problem.split('\n')
                        problem_title = problem_lines[0] if len(problem_lines) > 0 else "Problem:"
                        reason_text = '\n'.join(problem_lines[1:]) if len(problem_lines) > 1 else ""
                        
                        # Problem line
                        story.append(Paragraph(f"• <b>{problem_title}</b>", bullet_style))
                        
                        # Reason line (if exists)
                        if reason_text:
                            story.append(Paragraph(f"• <b>Reason:</b> {reason_text.replace('Reason: ', '')}", reason_style))
                    else:
                        # Legacy format - single problem line
                        story.append(Paragraph(f"• <b>Problem:</b> {issue.problem}", bullet_style))
                    
                    # Fix
                    story.append(Paragraph(f"• <b>Fix:</b> {issue.fix}", bullet_style))
                    
                    story.append(Spacer(1, 12))
                
                story.append(Spacer(1, 20))  # Extra space between line groups
        
        # Summary section
        story.append(Paragraph("✅ Summary", heading_style))
        
        # Build summary items based on what was actually found
        summary_content = []
        
        if summary.get('verb_tense_consistency', 0) > 0:
            count = summary['verb_tense_consistency']
            summary_content.append(f"• Verb tense &amp; agreement: {count} issue{'s' if count != 1 else ''} (tense consistency, subject-verb agreement)")
        
        if summary.get('awkward_phrasing', 0) > 0:
            count = summary['awkward_phrasing']
            summary_content.append(f"• Style &amp; clarity: {count} issue{'s' if count != 1 else ''} (awkward phrasing, unclear constructions)")
        
        if summary.get('redundancy', 0) > 0:
            count = summary['redundancy']
            summary_content.append(f"• Wordiness &amp; redundancy: {count} issue{'s' if count != 1 else ''} (repetitive phrases, unnecessary words)")
        
        if summary.get('grammar_punctuation', 0) > 0:
            count = summary['grammar_punctuation']
            summary_content.append(f"• Grammar &amp; punctuation: {count} issue{'s' if count != 1 else ''} (commas, quotation marks, apostrophes, spelling)")
        
        if summary_content:
            story.append(Paragraph("The main issues found in your document:", normal_style))
            for item in summary_content:
                story.append(Paragraph(item, normal_style))
        else:
            story.append(Paragraph("No issues found in your document.", normal_style))
        
        # Build PDF
        doc.build(story)
        
        return output_path
