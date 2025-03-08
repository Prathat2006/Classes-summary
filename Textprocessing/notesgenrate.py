import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.enums import TA_CENTER
import re
from Textprocessing.llminit import LLMManager

class NoteGeneratorAgent:
    def __init__(self, llm_manager, fallback_order):
        self.llm_manager = llm_manager
        self.fallback_order = fallback_order
        self.prompt = PromptTemplate(
            input_variables=["summary"],
            template="""You are an expert note-taking assistant. Given the following lecture summary, generate a detailed note in a structured format suitable for a professional PDF document. Use the following guidelines:
            - Start with a centered 'Lecture Title' derived from the summary content (infer if not explicit), without hashtags or extra symbols.
            - Include a centered section titled 'Introduction' providing a brief overview based on the summary.
            - Create a centered section titled 'Detailed Explanation' expanding on the summary with clear, step-by-step details.
            - Use '•' for main points, 'o' for second-level points, and '■' for third-level points.
            - Use **text** to emphasize key terms or concepts in bold, and _text_ for italicized emphasis where appropriate.
            - Include a centered section titled 'Important Points' summarizing key takeaways in bullet points.
            - End with a centered 'Conclusion' section tying the content together.
            - Avoid using hashtags or any markup other than ** for bold and _ for italic.
            - Ensure the tone is formal, educational, and clear for a student audience.
            Here is the lecture summary:
            {summary}
            """
        )

    def generate_note(self, summary, progress_callback=None):
        chain_input = self.prompt.format(summary=summary.strip())
        
        # Let the caller know we'll use 50% of progress for content generation
        # Track how much progress has been reported
        reported_progress = 0
        
        # Generate note content (up to 45% of progress)
        if progress_callback:
            # Report some initial progress for responsiveness
            progress_callback(5)
            reported_progress = 5
            
        note = self.llm_manager.invoke_with_fallback(
            self.llm_manager.setup_llm_with_fallback(self.fallback_order),
            self.fallback_order,
            chain_input
        )
        
        # Report we've completed content generation
        if progress_callback and reported_progress < 50:
            progress_callback(50 - reported_progress)
            reported_progress = 50

        if not note.strip():
            return "Error: Note could not be generated."
        return note

def update_pdf_file(file_path, note_text, progress_callback=None):
    doc = SimpleDocTemplate(file_path, pagesize=letter, leftMargin=0.75*inch, rightMargin=0.75*inch, topMargin=1*inch, bottomMargin=1*inch)
    styles = getSampleStyleSheet()

    heading_style = ParagraphStyle('Heading1', parent=styles['Heading1'], fontSize=14, spaceAfter=12, textColor=colors.darkblue, fontName='Helvetica-Bold', alignment=TA_CENTER)
    subheading_style = ParagraphStyle('Heading2', parent=styles['Heading2'], fontSize=12, spaceAfter=10, textColor=colors.black, fontName='Helvetica-Bold', alignment=TA_CENTER)
    body_style = ParagraphStyle('BodyText', parent=styles['Normal'], fontSize=10, spaceAfter=6, leading=12, fontName='Helvetica')
    bullet_style = ParagraphStyle('Bullet', parent=body_style, leftIndent=20, bulletIndent=10, spaceAfter=4, bulletFontName='Helvetica', bulletFontSize=10, bulletText='•')
    nested_bullet_style = ParagraphStyle('NestedBullet', parent=body_style, leftIndent=40, bulletIndent=30, spaceAfter=4, bulletFontName='Helvetica', bulletFontSize=10, bulletText='o')
    nested_bullet_style_2 = ParagraphStyle('NestedBullet2', parent=body_style, leftIndent=60, bulletIndent=50, spaceAfter=4, bulletFontName='Symbol', bulletFontSize=10, bulletText='■')

    content = []
    lines = note_text.split("\n")
    total_lines = len([line for line in lines if line.strip()])
    if total_lines == 0:
        total_lines = 1  # Avoid division by zero
        
    # Track progress for PDF building (starts at 50%)
    lines_processed = 0
    total_reported = 0

    # Build PDF with progress (50% of total progress)
    for i, line in enumerate(lines):
        line = line.strip()
        if not line:
            content.append(Spacer(1, 0.1*inch))
            continue

        lines_processed += 1
        line = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', line)
        line = re.sub(r'_(.*?)_', r'<i>\1</i>', line)

        if line.startswith("Lecture Title:"):
            content.append(Paragraph(line.lstrip("Lecture Title:").strip(), heading_style))
            content.append(Spacer(1, 0.2*inch))
        elif any(line.startswith(h) for h in ["Introduction", "Detailed Explanation", "Important Points", "Conclusion"]):
            content.append(Paragraph(line, subheading_style))
            content.append(Spacer(1, 0.05*inch))
        elif line.startswith("• "):
            content.append(Paragraph(line.lstrip("• ").strip(), bullet_style))
        elif line.startswith("o "):
            content.append(Paragraph(line.lstrip("o ").strip(), nested_bullet_style))
        elif line.startswith("■ ") or line.startswith("□ "):
            content.append(Paragraph(line.lstrip("■ ").lstrip("□ ").strip(), nested_bullet_style_2))
        else:
            content.append(Paragraph(line, body_style))
        
        # Update progress periodically, not on every line to avoid small fractional updates
        if progress_callback and lines_processed % max(1, int(total_lines/10)) == 0:
            # Calculate how much progress to report based on lines processed
            progress_to_report = int((lines_processed / total_lines) * 50)
            increment = progress_to_report - total_reported
            if increment > 0:
                progress_callback(increment)
                total_reported = progress_to_report
    
    # Ensure we report any remaining progress
    if progress_callback and total_reported < 50:
        progress_callback(50 - total_reported)

    doc.build(content)
    print(f"Detailed note saved as PDF at: {file_path}")

def lecture_note_generator(summary, output_path=None, fallback_order=None, progress_callback=None):
    llm_manager = LLMManager()
    llm_instances = llm_manager.setup_llm_with_fallback(fallback_order)
    if not llm_instances:
        raise Exception("No LLMs available for processing.")

    agent = NoteGeneratorAgent(llm_manager, fallback_order or llm_manager.DEFAULT_FALLBACK_ORDER)
    detailed_note = agent.generate_note(summary, progress_callback)
    # print("\nGenerated Detailed Note:\n")

    # if output_path is None:
    #     output_path = "Detailed_Lecture_Note.pdf"
    
    update_pdf_file(output_path, detailed_note, progress_callback)

    return detailed_note