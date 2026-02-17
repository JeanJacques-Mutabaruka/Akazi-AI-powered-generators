"""
AKAZI CV Generator V2 - ADAPTÉ au nouveau format JSON/YAML
Structure avec document_metadata, header, skills_table, experience_table
"""

from pathlib import Path
from typing import Dict, Any, Optional, List
from docx import Document
from docx.shared import Pt, RGBColor, Cm
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import json
import yaml
from docx.shared import Length

class AkaziCVGenerator:
    """Générateur CV AKAZI - Adapté nouveau format avec document_metadata"""
    
    COLOR_RED = RGBColor(192, 0, 0)
    COLOR_BLUE = RGBColor(0, 32, 96)
    COLOR_GOLD = RGBColor(204, 153, 0)
    COLOR_ORANGE = RGBColor(255, 140, 0)
    COLOR_BLACK = RGBColor(0, 0, 0)
    
    def __init__(self, input_file: Path, output_file: Path, **kwargs):
        self.input_file = input_file
        self.output_file = output_file
        self.data: Optional[Dict] = None
        self.doc: Optional[Document] = None
    

    def _calculate_dynamic_widths(self):
        """Calcule dynamiquement les largeurs en EMU (robuste multi-versions)"""
        section = self.doc.sections[0]

        usable_width = (section.page_width - section.left_margin - section.right_margin )

        # Selon version docx, usable_width peut être int ou Length
        if hasattr(usable_width, "emu"):
            usable_emu = usable_width.emu
        else:
            usable_emu = int(usable_width)

        left_emu = int(usable_emu * 0.21)
        right_emu = int(usable_emu * 0.79)

        self.left_col_width = Length(left_emu)
        self.right_col_width = Length(right_emu)

    def _set_fixed_table_layout(self, table, col_widths):
        """Force le layout fixe et applique largeurs colonnes + cellules"""
        table.autofit = False

        tbl = table._tbl
        tblPr = tbl.tblPr
        tblLayout = OxmlElement('w:tblLayout')
        tblLayout.set(qn('w:type'), 'fixed')
        tblPr.append(tblLayout)

        for i, width in enumerate(col_widths):
            table.columns[i].width = width

        for row in table.rows:
            for i, width in enumerate(col_widths):
                row.cells[i].width = width

    def _apply_standard_paragraph_format(self, para,int_space_before=3,int_space_after=3,):
        pf = para.paragraph_format
        pf.space_before = Pt(int_space_before)
        pf.space_after = Pt(int_space_after)
      

    def load_data(self):
        """Charge JSON ou YAML"""
        with open(self.input_file, 'r', encoding='utf-8') as f:
            if self.input_file.suffix == '.json':
                self.data = json.load(f)
            else:
                self.data = yaml.safe_load(f)
    
    def validate_data(self):
        """Valide structure avec document_metadata"""
        required = ['document_metadata', 'header', 'skills_table', 'experience_table']
        missing = [k for k in required if k not in self.data]
        if missing:
            raise ValueError(f"Missing keys: {missing}")
        
        # Vérifier metadata
        metadata = self.data['document_metadata']
        if metadata.get('format_code') != 'AKAZI_V1':
            raise ValueError(f"Wrong format_code: {metadata.get('format_code')}")
        
        return True
    
    def setup_document(self):
        """Initialize Word document"""
        self.doc = Document()
        
        style = self.doc.styles['Normal']
        style.font.name = 'Century Gothic'
        style.font.size = Pt(9)
        
        for section in self.doc.sections:
            section.top_margin = Cm(1.27)
            section.bottom_margin = Cm(1.27)
            section.left_margin = Cm(1.27)
            section.right_margin = Cm(1.27)
        
        self._calculate_dynamic_widths()

    def generate_header(self):
        """Génère header depuis data['header']"""
        header = self.data['header']
        
        # Line 1: INITIALES - TITRE - X années (RED)
        line1 = self.doc.add_paragraph()
        line1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        text = f"{header['initials']} - {header['title']} - {header['years_of_experience']}"
        run1 = line1.add_run(text)
        run1.font.name = 'Century Gothic'
        run1.font.size = Pt(11)
        run1.font.color.rgb = self.COLOR_RED
        run1.bold = True
        
        # Line 2: TJM + Contact (BLUE + GOLD)
        line2 = self.doc.add_paragraph()
        line2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        tjm = header.get('daily_rate', '----------')
        run2a = line2.add_run(f"TJM souhaité : {tjm}€ - Contact : Janvier au 0783388802")
        run2a.font.name = 'Century Gothic'
        run2a.font.size = Pt(11)
        run2a.font.color.rgb = self.COLOR_BLUE
        run2a.bold = True
        
        run2c = line2.add_run(" ou sur ")
        run2c.font.name = 'Century Gothic'
        run2c.font.size = Pt(11)
        run2c.font.color.rgb = self.COLOR_BLUE
        run2c.bold = True

        run2b = line2.add_run("contact@akazi.fr")
        run2b.font.name = 'Century Gothic'
        run2b.font.size = Pt(11)
        run2b.font.color.rgb = self.COLOR_GOLD
        run2b.bold = True
        
    
    def generate_skills_table(self):
        """Génère tableau compétences depuis data['skills_table']"""
        skills = self.data['skills_table']
        
        table = self.doc.add_table(rows=5, cols=2)
        table.style = 'Table Grid'
        self._set_fixed_table_layout(table, [self.left_col_width, self.right_col_width])

        
        # Row 0: Functional skills
        self._populate_skill_row(
            table.rows[0],
            "COMPÉTENCES\nFONCTIONNELLES",
            skills['functional_skills']['summary'],
            skills['functional_skills']['details']
        )
        
        # Row 1: Technical skills
        self._populate_skill_row(
            table.rows[1],
            "COMPÉTENCES\nTECHNIQUES",
            skills['technical_skills']['summary'],
            skills['technical_skills']['details']
        )
        
        # Row 2: Education
        self._populate_education_row(table.rows[2], skills.get('education', []))
        
        # Row 3: Certifications
        self._populate_certifications_row(table.rows[3], skills.get('certifications', []))
        
        # Row 4: Languages
        self._populate_languages_row(table.rows[4], skills.get('languages', []))
    
    def _populate_skill_row(self, row, title: str, summary: str, details: List[Dict]):
        """Populate skill row (functional or technical)"""
        # Left cell
        left_cell = row.cells[0]
        left_para = left_cell.paragraphs[0]
        left_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        left_run = left_para.add_run(title)
        left_run.font.name = 'Century Gothic'
        left_run.font.size = Pt(9)
        left_run.font.color.rgb = self.COLOR_RED
        left_run.bold = True
        left_cell.vertical_alignment = 1
        
        # Right cell
        right_cell = row.cells[1]
        right_cell.text = ''
        
        # Summary (blue, bold)
        if summary:
            summary_para = right_cell.add_paragraph()
            self._apply_standard_paragraph_format(summary_para)

            summary_para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            summary_run = summary_para.add_run(summary)
            summary_run.font.name = 'Century Gothic'
            summary_run.font.size = Pt(9)
            summary_run.font.color.rgb = self.COLOR_BLUE
            summary_run.bold = True
        
        # Details (bullets)
        for detail in details:
            text = detail.get('text', '')
            bold_prefix = detail.get('bold_prefix', '')
            self._add_bullet_item(right_cell, text, bold_prefix)
    
    def _populate_education_row(self, row, education: List[Dict]):
        """Populate education row"""
        left_cell = row.cells[0]
        left_para = left_cell.paragraphs[0]
        left_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        left_run = left_para.add_run("FORMATION &\nDIPLOMES")
        left_run.font.name = 'Century Gothic'
        left_run.font.size = Pt(9)
        left_run.font.color.rgb = self.COLOR_RED
        left_run.bold = True
        left_cell.vertical_alignment = 1
        
        right_cell = row.cells[1]
        right_cell.text = ''
        
        for edu in education:
            year = edu.get('year', '')
            degree = edu.get('degree', '')
            institution = edu.get('institution', '')
            text = f"{year} : {degree} - {institution}"
            self._add_bullet_item(right_cell, text)
    
    def _populate_certifications_row(self, row, certifications: List):
        """Populate certifications row"""
        left_cell = row.cells[0]
        left_para = left_cell.paragraphs[0]
        left_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        left_run = left_para.add_run("CERTIFICATIONS")
        left_run.font.name = 'Century Gothic'
        left_run.font.size = Pt(9)
        left_run.font.color.rgb = self.COLOR_RED
        left_run.bold = True
        left_cell.vertical_alignment = 1
        
        right_cell = row.cells[1]
        right_cell.text = ''
        
        for cert in certifications:
            if isinstance(cert, dict):
                text = cert.get('text', str(cert))
            else:
                text = str(cert)
            self._add_bullet_item(right_cell, text)
    
    def _populate_languages_row(self, row, languages: List[Dict]):
        """Populate languages row"""
        left_cell = row.cells[0]
        left_para = left_cell.paragraphs[0]
        left_para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        left_run = left_para.add_run("LANGUES")
        left_run.font.name = 'Century Gothic'
        left_run.font.size = Pt(9)
        left_run.font.color.rgb = self.COLOR_RED
        left_run.bold = True
        left_cell.vertical_alignment = 1
        
        right_cell = row.cells[1]
        right_cell.text = ''
        
        for lang in languages:
            language = lang.get('language', '')
            level = lang.get('level', '')
            inferred = lang.get('inferred', False)
            text = f"{language} : {level}"
            color = self.COLOR_ORANGE if inferred else self.COLOR_BLACK
            self._add_bullet_item(right_cell, text, color=color)
    
    def generate_experiences(self):
        """Génère expériences depuis data['experience_table']"""
        experiences = self.data.get('experience_table', [])
        
        if not experiences:
            return
        
        # Ajouter titre "EXPERIENCE PROFESSIONNELLE" (ROUGE, centré, bold)
        self._add_experience_section_title()
        
        # Générer chaque expérience
        for exp in experiences:
            self._generate_single_experience(exp)
    
    def _add_experience_section_title(self):
        """Ajoute le titre de section EXPERIENCE PROFESSIONNELLE"""
        # Créer tableau avec 1 ligne, 1 colonne pour le titre
        self.doc.add_paragraph()
        title_table = self.doc.add_table(rows=1, cols=1)
        title_table.autofit = False
        title_table.style = 'Table Grid'
        
        # Cellule du titre
        cell = title_table.rows[0].cells[0]
        para = cell.paragraphs[0]
        para.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
        run = para.add_run("EXPERIENCE PROFESSIONNELLE")
        run.font.name = 'Century Gothic'
        run.font.size = Pt(11)
        run.font.color.rgb = self.COLOR_RED
        run.bold = True
        
        # Espace après le titre
    
    def _generate_single_experience(self, exp: Dict):
        """Generate single experience with NEW 2-column structure (1 row, 2 merged cells)"""

        table = self.doc.add_table(rows=1, cols=2)
        table.style = 'Table Grid'

        # Désactiver l'autofit
        table.autofit = False

        # Forcer layout fixed
        tbl = table._tbl
        tblPr = tbl.tblPr
        tblLayout = OxmlElement('w:tblLayout')
        tblLayout.set(qn('w:type'), 'fixed')
        tblPr.append(tblLayout)

        # Définir largeur des colonnes
        self._set_fixed_table_layout(table, [self.left_col_width, self.right_col_width])


        # IMPORTANT : définir aussi largeur des cellules
        for row in table.rows:
            row.cells[0].width = Cm(3.5)
            row.cells[1].width = Cm(13.0)

        # Récupérer données
        company = exp.get('company', 'N/A')
        period = exp.get('period', {})
        period_formatted = period.get('formatted', 'N/A')
        title = exp.get('title', 'N/A')
        context = exp.get('mission_context', '')
        tasks = exp.get('tasks', [])
        tech_env = exp.get('technical_environment', [])
        
        # Cellule 1 (Colonne gauche): Company + Period
        cell_left = table.rows[0].cells[0]
        self._populate_left_cell(cell_left, company, period_formatted)
        
        # Cellule 2 (Colonne droite): Title + Contexte + Tâches + Tech
        cell_right = table.rows[0].cells[1]
        self._populate_right_cell(cell_right, title, context, tasks, tech_env)
        
    
    def _populate_left_cell(self, cell, company: str, period: str):
        """Colonne gauche: Company + Period (21%)"""
        cell.text = ''  # Clear
        cell.vertical_alignment = 0  # Centré verticalement
        
        # Company (BLEU, bold, centré)
        para_company = cell.add_paragraph()
        self._apply_standard_paragraph_format(para_company)

        para_company.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_company = para_company.add_run(company)
        run_company.font.name = 'Century Gothic'
        run_company.font.size = Pt(9)
        run_company.font.color.rgb = self.COLOR_BLUE
        run_company.bold = True
        
        # Ligne vide pour espacement
        cell.add_paragraph()
        
        # Period (BLEU, bold, centré, entre parenthèses)
        para_period = cell.add_paragraph()
        self._apply_standard_paragraph_format(para_period)

        para_period.alignment = WD_ALIGN_PARAGRAPH.CENTER
        run_period = para_period.add_run(f"({period})")
        run_period.font.name = 'Century Gothic'
        run_period.font.size = Pt(9)
        run_period.font.color.rgb = self.COLOR_BLUE
        run_period.bold = True
    
    def _populate_right_cell(self, cell, title: str, context: str, tasks: List[str], tech_env: List[Dict]):
        """Colonne droite: Title + Contexte + Tâches + Tech (79%)"""
        cell.text = ''  # Clear
        
        # 1. TITLE (BLEU, bold, 10pt)
        para_title = cell.add_paragraph()
        self._apply_standard_paragraph_format(para_title,6,6)

        run_title = para_title.add_run(title)
        run_title.font.name = 'Century Gothic'
        run_title.font.size = Pt(10)
        run_title.font.color.rgb = self.COLOR_BLUE
        run_title.bold = True
                
        # 2. CONTEXTE DE LA MISSION
        context_header = cell.add_paragraph()
        self._apply_standard_paragraph_format(context_header,3,3)

        context_header.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        context_header.paragraph_format.left_indent = Cm(0.5)
        
        label_context = context_header.add_run("■ Contexte de la mission : ")
        label_context.font.name = 'Century Gothic'
        label_context.font.size = Pt(9)
        label_context.font.color.rgb = self.COLOR_BLACK
        label_context.bold = True

        context_para_text = cell.add_paragraph()
        context_para_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        context_text = context_para_text.add_run(context)
        context_text.italic = True
        context_text.font.size = Pt(9)
        context_text.font.color.rgb = self.COLOR_BLACK

        context_para_pf = context_para_text.paragraph_format
        context_para_pf.left_indent = Cm(1.0)
        context_para_pf.first_line_indent = Cm(0.0)
        context_para_pf.space_before = Pt(6)
        context_para_pf.space_after = Pt(6)
        
        # 3. TÂCHES
        para_tasks_label = cell.add_paragraph()
        self._apply_standard_paragraph_format(para_tasks_label)
        para_tasks_label.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        para_tasks_label.paragraph_format.left_indent = Cm(0.5)
        
        label_tasks = para_tasks_label.add_run("■ Tâches :")
        label_tasks.font.name = 'Century Gothic'
        label_tasks.font.size = Pt(9)
        label_tasks.font.color.rgb = self.COLOR_BLACK
        label_tasks.bold = True
        
        # Ajouter chaque tâche comme bullet
        for task in tasks:
            self._add_bullet_item(cell, task,flt_left_indent = 1.5)
        
        # Espace
        cell.add_paragraph()
        
        # 4. ENVIRONNEMENTS / OUTILS ET TECHNOLOGIES
        para_tech = cell.add_paragraph()
        self._apply_standard_paragraph_format(para_tech)

        para_tech.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        para_tech.paragraph_format.left_indent = Cm(0.5)
        
        label_tech = para_tech.add_run("■ Environnements / Outils et technologies : ")
        label_tech.font.name = 'Century Gothic'
        label_tech.font.size = Pt(9)
        label_tech.font.color.rgb = self.COLOR_BLACK
        label_tech.bold = True
        
        # Extraire et joindre les technologies
        tech_texts = []
        for tech in tech_env:
            if isinstance(tech, dict):
                tech_texts.append(tech.get('technologies', ''))
            else:
                tech_texts.append(str(tech))
        
        tech_text = ', '.join(tech_texts)
        # run_tech = para_tech.add_run(tech_text)
        # run_tech.font.name = 'Century Gothic'
        # run_tech.font.size = Pt(9)
        # run_tech.font.color.rgb = self.COLOR_BLACK
        tech_para_text = cell.add_paragraph()
        tech_para_text.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        tech_para_text.style = 'List Bullet 2'
        tech_text = tech_para_text.add_run(tech_text)
        tech_text.bold = True
        tech_text.font.size = Pt(9)
        tech_text.font.color.rgb = self.COLOR_BLACK

        tech_para_pf = tech_para_text.paragraph_format
        tech_para_pf.left_indent = Cm(1.0)
        tech_para_pf.first_line_indent = Cm(0.0)
        tech_para_pf.space_before = Pt(6)
        tech_para_pf.space_after = Pt(6)
        



    def _add_bullet_item(self, cell, text: str, bold_prefix: str = '', color: RGBColor = None, flt_left_indent:float = 0.5, flt_1stline_indent:float = 0.5):
        if color is None:
            color = self.COLOR_BLACK

        para = cell.add_paragraph()
        para.style = 'List Bullet'
        para.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

        pf = para.paragraph_format
        pf.left_indent = Cm(flt_left_indent)
        pf.first_line_indent = Cm(-flt_1stline_indent)
        pf.space_before = Pt(3)
        pf.space_after = Pt(3)

        if bold_prefix:
            bold_run = para.add_run(bold_prefix + " : ")
            bold_run.font.name = 'Century Gothic'
            bold_run.font.size = Pt(9)
            bold_run.font.color.rgb = color
            bold_run.bold = True

            rest = text.replace(bold_prefix + " : ", "").replace(bold_prefix + ": ", "")
            normal_run = para.add_run(rest)
            normal_run.font.name = 'Century Gothic'
            normal_run.font.size = Pt(9)
            normal_run.font.color.rgb = color
        else:
            run = para.add_run(text)
            run.font.name = 'Century Gothic'
            run.font.size = Pt(9)
            run.font.color.rgb = color
    
    def save_document(self):
        """Save document"""
        self.doc.save(str(self.output_file))
    
    def generate(self):
        """Main generation method"""
        self.load_data()
        self.validate_data()
        self.setup_document()
        self.generate_header()
        self.generate_skills_table()
        self.generate_experiences()
        self.save_document()
