"""
MC2I CV Generator V2 - ADAPTÉ au nouveau format JSON/YAML
Structure avec document_metadata, introduction, languages, expertise, professional_experiences
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from datetime import datetime
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import json
import yaml

class MC2ICVGenerator:
    """Générateur CV MC2I - Adapté nouveau format avec document_metadata"""
    
    COLOR_COMPANY = RGBColor(221, 0, 97)
    COLOR_MISSION = RGBColor(0, 106, 158)
    COLOR_TEXT = RGBColor(87, 88, 86)
    COLOR_ORANGE = RGBColor(255, 140, 0)
    COLOR_SEPARATOR = RGBColor(221, 0, 97)
    
    def __init__(self, input_file: Path, output_file: Path, **kwargs):
        self.input_file = input_file
        self.output_file = output_file
        self.data: Optional[Dict] = None
        self.doc: Optional[Document] = None
    
    def load_data(self):
        """Charge JSON ou YAML"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            if self.input_file.suffix == '.json':
                self.data = json.load(f)
            else:
                self.data = yaml.safe_load(f)
    
    def validate_data(self):
        """Valide structure MC2I avec document_metadata"""
        required = ['document_metadata', 'introduction', 'professional_experiences']
        missing = [k for k in required if k not in self.data]
        if missing:
            raise ValueError(f"Missing keys: {missing}")
        
        metadata = self.data['document_metadata']
        if metadata.get('format_code') != 'MC2I_V1':
            raise ValueError(f"Wrong format_code: {metadata.get('format_code')}")
        
        return True
    
    def setup_document(self):
        """Initialize Word document with MC2I formatting"""
        self.doc = Document()
        
        style = self.doc.styles['Normal']
        style.font.name = 'Lato'
        style.font.size = Pt(10)
        style.font.color.rgb = self.COLOR_TEXT
        
        paragraph_format = style.paragraph_format
        paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        paragraph_format.line_spacing = 1.15
        
        for section in self.doc.sections:
            section.top_margin = Cm(2.54)
            section.bottom_margin = Cm(2.54)
            section.left_margin = Cm(2.54)
            section.right_margin = Cm(2.54)
    
    def generate_header(self):
        """Génère header avec nom et titre"""
        # Extract name from experience_summary or use candidate_id
        experience_summary = self.data.get('experience_summary', [])
        if experience_summary and len(experience_summary) > 0:
            title = experience_summary[0].get('title', 'CONSULTANT')
        else:
            title = 'CONSULTANT'
        
        # Get specialty from introduction
        intro = self.data.get('introduction', {})
        specialty = intro.get('experience_summary', '')[:100]  # First 100 chars
        
        # Name (16pt, bold)
        name_para = self.doc.add_paragraph()
        name_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        name_run = name_para.add_run("CONSULTANT DATA")
        name_run.font.name = 'Lato'
        name_run.font.size = Pt(16)
        name_run.font.color.rgb = self.COLOR_TEXT
        name_run.bold = True
        
        # Specialty (14pt, bold, company color)
        title_para = self.doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        title_run = title_para.add_run(title if title else "DATA ANALYST")
        title_run.font.name = 'Lato'
        title_run.font.size = Pt(14)
        title_run.font.color.rgb = self.COLOR_COMPANY
        title_run.bold = True
        
        # Years of experience
        exp_sum = self.data.get('experience_summary', [])
        total_months = sum(e.get('duration_months', 0) for e in exp_sum)
        years = total_months // 12
        
        exp_para = self.doc.add_paragraph()
        exp_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        exp_run = exp_para.add_run(f"{years} années d'expérience")
        exp_run.font.name = 'Lato'
        exp_run.font.size = Pt(10)
        exp_run.font.color.rgb = self.COLOR_TEXT
    
    def add_horizontal_separator(self):
        """Add horizontal line separator"""
        para = self.doc.add_paragraph()
        pPr = para._element.get_or_add_pPr()
        pBdr = OxmlElement('w:pBdr')
        
        bottom = OxmlElement('w:bottom')
        bottom.set(qn('w:val'), 'single')
        bottom.set(qn('w:sz'), '6')
        bottom.set(qn('w:space'), '1')
        bottom.set(qn('w:color'), 'DD0061')
        
        pBdr.append(bottom)
        pPr.append(pBdr)
    
    def generate_introduction(self):
        """Génère introduction (4 paragraphes)"""
        intro = self.data.get('introduction', {})
        
        # Para 1: Experience summary
        exp_sum = intro.get('experience_summary', '')
        if exp_sum:
            para1 = self.doc.add_paragraph()
            para1.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run1 = para1.add_run(exp_sum)
            run1.font.size = Pt(10)
            run1.font.color.rgb = self.COLOR_TEXT
        
        # Para 2: Technical skills summary
        tech_sum = intro.get('technical_skills_summary', '')
        if tech_sum:
            para2 = self.doc.add_paragraph()
            para2.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run2 = para2.add_run(tech_sum)
            run2.font.size = Pt(10)
            run2.font.color.rgb = self.COLOR_TEXT
        
        # Para 3: Functional skills summary
        func_sum = intro.get('functional_skills_summary', '')
        if func_sum:
            para3 = self.doc.add_paragraph()
            para3.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run3 = para3.add_run(func_sum)
            run3.font.size = Pt(10)
            run3.font.color.rgb = self.COLOR_TEXT
        
        # Para 4: Conclusion
        conclusion = intro.get('conclusion', {})
        conclusion_text = conclusion.get('text', '')
        if conclusion_text:
            para4 = self.doc.add_paragraph()
            para4.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            run4 = para4.add_run(conclusion_text)
            run4.font.size = Pt(10)
            run4.font.color.rgb = self.COLOR_TEXT
    
    def generate_languages(self):
        """Génère section langues"""
        self._add_section_title("LANGUES")
        
        languages = self.data.get('languages', [])
        for lang in languages:
            language = lang.get('language', '')
            level = lang.get('level', '')
            text = f"{language} : {level}"
            
            para = self.doc.add_paragraph()
            para.style = 'List Bullet'
            run = para.add_run(text)
            run.font.size = Pt(10)
            run.font.color.rgb = self.COLOR_TEXT
    
    def generate_education(self):
        """Génère section formation"""
        self._add_section_title("FORMATION")
        
        education = self.data.get('education', [])
        for edu in education:
            year = edu.get('year', '')
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            text = f"{year} : {degree} - {institution}"
            
            para = self.doc.add_paragraph()
            para.style = 'List Bullet'
            run = para.add_run(text)
            run.font.size = Pt(10)
            run.font.color.rgb = self.COLOR_TEXT
    
    def generate_expertise(self):
        """Génère section expertises"""
        self._add_section_title("EXPERTISES, OUTILS ET TECHNOLOGIES")
        
        expertise = self.data.get('expertise', {})
        
        # Expertises list
        expertises = expertise.get('expertises', [])
        for exp in expertises:
            para = self.doc.add_paragraph()
            para.style = 'List Bullet'
            run = para.add_run(exp)
            run.font.size = Pt(10)
            run.font.color.rgb = self.COLOR_TEXT
        
        # Masteries list
        masteries = expertise.get('masteries', [])
        if masteries:
            # Group masteries in paragraph
            para = self.doc.add_paragraph()
            para.style = 'List Bullet'
            run = para.add_run(', '.join(masteries))
            run.font.size = Pt(10)
            run.font.color.rgb = self.COLOR_TEXT
    
    def generate_experiences(self):
        """Génère expériences professionnelles"""
        self._add_section_title("EXPÉRIENCES PROFESSIONNELLES")
        
        experiences = self.data.get('professional_experiences', [])
        
        for idx, exp in enumerate(experiences):
            self._generate_single_experience(exp)
            
            if idx < len(experiences) - 1:
                self.add_horizontal_separator()
    
    def _generate_single_experience(self, exp: Dict):
        """Generate single experience MC2I format"""
        # COMPANY (all caps, small caps, company color, 14pt, bold)
        company = exp.get('company', 'N/A').upper()
        company_para = self.doc.add_paragraph()
        company_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        company_run = company_para.add_run(company)
        company_run.font.name = 'Lato'
        company_run.font.size = Pt(14)
        company_run.font.color.rgb = self.COLOR_COMPANY
        company_run.bold = True
        company_run.font.small_caps = True
        
        # TITLE (small caps, mission color, 14pt, bold)
        title = exp.get('title', 'N/A')
        title_para = self.doc.add_paragraph()
        title_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        title_run = title_para.add_run(title)
        title_run.font.name = 'Lato'
        title_run.font.size = Pt(14)
        title_run.font.color.rgb = self.COLOR_MISSION
        title_run.bold = True
        title_run.font.small_caps = True
        
        # PERIOD (small caps, mission color, 10pt)
        period = exp.get('period', {})
        period_formatted = period.get('formatted', 'N/A')
        period_para = self.doc.add_paragraph()
        period_para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        period_run = period_para.add_run(period_formatted)
        period_run.font.name = 'Lato'
        period_run.font.size = Pt(10)
        period_run.font.color.rgb = self.COLOR_MISSION
        period_run.font.small_caps = True
        
        # Context
        context = exp.get('context', '')
        if context:
            context_para = self.doc.add_paragraph()
            context_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            context_run = context_para.add_run(context)
            context_run.font.size = Pt(10)
            context_run.font.color.rgb = self.COLOR_TEXT
        
        # ACTIVITÉS (bold keyword)
        activities_label = self.doc.add_paragraph()
        activities_run = activities_label.add_run("Activités :")
        activities_run.font.size = Pt(10)
        activities_run.font.color.rgb = self.COLOR_TEXT
        activities_run.bold = True
        
        # Activities list
        activities = exp.get('activities', [])
        for activity in activities:
            task_para = self.doc.add_paragraph()
            task_para.style = 'List Bullet'
            task_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            task_run = task_para.add_run(activity)
            task_run.font.size = Pt(10)
            task_run.font.color.rgb = self.COLOR_TEXT
        
        # DOMAINES (bold keyword)
        domains_label = self.doc.add_paragraph()
        domains_run = domains_label.add_run("Domaines :")
        domains_run.font.size = Pt(10)
        domains_run.font.color.rgb = self.COLOR_TEXT
        domains_run.bold = True
        
        # Functional domains
        domains = exp.get('functional_domains', [])
        for dom in domains:
            domain_text = dom.get('domain', '')
            domain_para = self.doc.add_paragraph()
            domain_para.style = 'List Bullet'
            domain_run = domain_para.add_run(domain_text)
            domain_run.font.size = Pt(10)
            domain_run.font.color.rgb = self.COLOR_TEXT
        
        # ENVIRONNEMENT TECHNIQUE (bold keyword)
        tech_label = self.doc.add_paragraph()
        tech_run = tech_label.add_run("Environnement technique :")
        tech_run.font.size = Pt(10)
        tech_run.font.color.rgb = self.COLOR_TEXT
        tech_run.bold = True
        
        # Technical environment
        tech_env = exp.get('technical_environment', [])
        tech_texts = []
        for tech in tech_env:
            if isinstance(tech, dict):
                tech_texts.append(tech.get('technologies', ''))
            else:
                tech_texts.append(str(tech))
        
        if tech_texts:
            tech_para = self.doc.add_paragraph()
            tech_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            tech_para_run = tech_para.add_run(', '.join(tech_texts))
            tech_para_run.font.size = Pt(10)
            tech_para_run.font.color.rgb = self.COLOR_TEXT
    
    def _add_section_title(self, title: str):
        """Add section title (bold, 12pt)"""
        para = self.doc.add_paragraph()
        para.alignment = WD_ALIGN_PARAGRAPH.LEFT
        run = para.add_run(title)
        run.font.name = 'Lato'
        run.font.size = Pt(12)
        run.font.color.rgb = self.COLOR_TEXT
        run.bold = True
    
    def save_document(self):
        """Save document"""
        self.doc.save(str(self.output_file))
    
    def generate(self):
        """Main generation method"""
        self.load_data()
        self.validate_data()
        self.setup_document()
        self.generate_header()
        self.add_horizontal_separator()
        self.generate_introduction()
        self.add_horizontal_separator()
        self.generate_languages()
        self.add_horizontal_separator()
        self.generate_education()
        self.add_horizontal_separator()
        self.generate_expertise()
        self.add_horizontal_separator()
        self.generate_experiences()
        self.save_document()
